#import mysql.connector
import sqlite3

#id = name[:3] + start + name[-3:] + days
class DBHelper:

    def __init__(self, dbname="leaves.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        
    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS mydb (user TEXT, pass TEXT, dept TEXT, admin TEXT, totalleave TEXT, remaining TEXT, chatid TEXT)"
        self.conn.execute(stmt)
        self.conn.commit()
        
    def login(self, user, passwd, chatid):
        cur = self.conn.cursor()
        stmt = "SELECT COUNT (*) FROM mydb WHERE user = ? AND pass = ?"
        args = (user, passwd)
        cur.execute(stmt, args)
        res = cur.fetchone()[0]
        if int(res) == 1:
            stmt = "SELECT admin,dept FROM mydb WHERE user = ? AND pass = ?"
            cur.execute(stmt, args)
            res = cur.fetchone()
            stmt = "UPDATE mydb SET chatid = ? WHERE user = ?"
            args = (chatid, user)
            cur.execute(stmt, args)
            self.conn.commit()
            cur.close()
            return res
        else:
            cur.close()
            return False
            
    def createuser(self, name, pin, dept, admin):
        cur = self.conn.cursor()
        stmt = "INSERT into mydb(user,pass,dept,admin,totalleave,remaining) VALUES (?, ?, ?, ?, '10', '10')"
        args = (name, pin, dept, admin)
        cur.execute(stmt, args)
        stmt = "CREATE TABLE IF NOT EXISTS approve_" + name + " (id TEXT, start TEXT, end TEXT, days TEXT, reason TEXT)"
        cur.execute(stmt)
        stmt = "CREATE TABLE IF NOT EXISTS apply_" + name + " (id TEXT, start TEXT, end TEXT, days TEXT, reason TEXT)"
        cur.execute(stmt)
        stmt = "CREATE TABLE IF NOT EXISTS reject_" + name + " (id TEXT, start TEXT, end TEXT, days TEXT, reason TEXT)"
        cur.execute(stmt)
        self.conn.commit()
        cur.close()
        
     
    def findnameinstance(self, name):
        cur = self.conn.cursor()
        stmt = "SELECT COUNT (*) FROM mydb WHERE user = ?"
        args = (name, )
        cur.execute(stmt, args)
        res = cur.fetchone()[0]
        return res
        
    def findnameinstance(self, name, dept):
        cur = self.conn.cursor()
        stmt = "SELECT COUNT (*) FROM mydb WHERE user = ? AND dept = ?"
        args = (name, dept)
        cur.execute(stmt, args)
        res = cur.fetchone()[0]
        return res
     
    def removeuser(self, name):
        cur = self.conn.cursor()
        stmt = "DELETE FROM mydb WHERE user = ?"
        args = (name, )
        cur.execute(stmt, args)
        stmt = "CREATE TABLE IF NOT EXISTS removed (id TEXT, start TEXT, end TEXT, days TEXT)"
        cur.execute(stmt)
        stmt = "INSERT INTO removed SELECT id,start,end,days FROM approve_" + name
        cur.execute(stmt)
        stmt = "DROP TABLE IF EXISTS approve_" + name
        cur.execute(stmt)
        stmt = "DROP TABLE IF EXISTS apply_" + name
        cur.execute(stmt)
        stmt = "DROP TABLE IF EXISTS reject_" + name
        cur.execute(stmt)
        self.conn.commit()
        cur.close()
        
    def close(self):
        self.conn.close()
        
    def checkpin(self, user, pin):
        cur = self.conn.cursor()
        stmt = "SELECT pass FROM mydb WHERE user = ?"
        args = (user, )
        cur.execute(stmt, args)
        res = cur.fetchone()[0]
        cur.close()
        return pin == res
        
    def updatepin(self, user, pin):
        cur = self.conn.cursor()
        stmt = "UPDATE mydb SET pass = ? WHERE user = ?"
        args = (pin, user, )
        cur.execute(stmt, args)
        self.conn.commit()
        cur.close()
        
    def checkleavedays(self, user):
        cur = self.conn.cursor()
        stmt = "SELECT remaining FROM mydb WHERE user = ?"
        args = (user, )
        cur.execute(stmt, args)
        res = cur.fetchone()[0]
        cur.close()
        return int(res)
        
    def genleaveid(self, user, start, days):
        return user[:3] + start + user[-3:] + days
        
    def applyleave(self, user, start, end, days, reason):
        remaining = self.checkleavedays(user)
        if remaining >= int(days):
            key = self.genleaveid(user, start, days)
            cur = self.conn.cursor()
            stmt = "INSERT INTO apply_" + user + " VALUES (?, ?, ?, ?, ?)"
            args = (key, start, end, days, reason)
            cur.execute(stmt, args)
            self.conn.commit()
            cur.close()
            return True
        else:
            return False
            
    def approve(self, user, id):
        cur = self.conn.cursor()
        stmt = "SELECT days FROM apply_" + user + " WHERE id = ?"
        args = (id, )
        cur.execute(stmt, args)
        remaining = self.checkleavedays(user) - int(cur.fetchone()[0])
        stmt = "UPDATE mydb SET remaining = ? WHERE user = ?"
        args2 = (str(remaining), user)
        cur.execute(stmt, args2)
        stmt = "INSERT INTO approve_" + user + " SELECT * FROM apply_" + name
        cur.execute(stmt)
        stmt = "DELETE FROM apply_" + user + " WHERE id = ?"
        cur.execute(stmt, args)
        self.conn.commit()
        cur.close()
        
    def findsuper(self, dept):
        cur = self.conn.cursor()
        stmt = "SELECT chatid FROM mydb WHERE dept = ? AND admin = 'Yes'"
        args = (dept, )
        cur.execute(stmt, args)
        res = cur.fetchone()[0]
        return res
        
        
    def test(self):
        cur = self.conn.cursor()
        stmt = "CREATE TABLE IF NOT EXISTS removed (user TEXT, dept TEXT)"
        cur.execute(stmt)
        stmt = stmt = "INSERT INTO removed SELECT user, dept FROM mydb"
        cur.execute(stmt)
        self.conn.commit()
        cur.close()
        
def main():
    db = DBHelper()
    res = db.test()
    db.close()


if __name__ == '__main__':
    main()


