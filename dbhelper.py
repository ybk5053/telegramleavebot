#import mysql.connector
import sqlite3
import datetime

#leaveid = name[:3] + start + name[-3:] + days
#leave table name = approve_user, reject_user, apply_user
#leave table cols = 0:id, 1:start, 2:end, 3:days, 4:reason

file_name = "leaves.sqlite" #sqlite file name

class DBHelper:

    def __init__(self):
        self.dbname = file_name
        self.conn = sqlite3.connect(file_name)
        
    def setup(self, user, passwd):
        stmt = "CREATE TABLE IF NOT EXISTS mydb (user TEXT, pass TEXT, dept TEXT, admin TEXT, totalleave TEXT, remaining TEXT, chatid TEXT)"
        self.conn.execute(stmt)
        stmt = "SELECT COUNT (*) FROM mydb"
        if self.conn.execute(stmt).fetchone()[0] < 1:
            stmt = "INSERT INTO mydb(user,pass,dept,admin) VALUES(?, ?, 'admin', 'Yes')"
            args = (user, passwd)
            self.conn.execute(stmt, args)
            self.conn.commit()
            return True
        return False
        
    def setupdepts(self, depts):
        stmt = "DROP TABLE IF EXISTS depts"
        self.conn.execute(stmt)
        stmt = "CREATE TABLE IF NOT EXISTS depts (name TEXT)"
        self.conn.execute(stmt)
        for dept in depts:
            stmt = "INSERT INTO depts VALUES(?)"
            args = (dept, )
            self.conn.execute(stmt, args)
        self.conn.commit()
        
    def getdepts(self): #return list name of all dept
        stmt = "SELECT name FROM depts"
        cur = self.conn.cursor()
        cur.execute(stmt)
        res = []
        for rows in cur.fetchall():
            res.append(rows[0])
        return res
        
        
    def login(self, user, passwd, chatid): ##return false if fail is user/pass check fail..else return (admin, dept) ##update chatid for leave status msg
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
            
    def createuser(self, name, pin, dept, admin): ##create req tables for user
        cur = self.conn.cursor()
        stmt = "INSERT INTO mydb(user,pass,dept,admin,totalleave,remaining) VALUES (?, ?, ?, ?, '10', '10')"
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
        
     
    def findnameinstance(self, name, dept=None):  ##check if name already exist return num>1 if exist
        if dept is None:  ##check everywhere
            cur = self.conn.cursor()
            stmt = "SELECT COUNT (*) FROM mydb WHERE user = ?"
            args = (name, )
            cur.execute(stmt, args)
            res = cur.fetchone()[0]
            cur.close()
            return res
        else: ##check within dept
            cur = self.conn.cursor()
            stmt = "SELECT COUNT (*) FROM mydb WHERE user = ? AND dept = ?"
            args = (name, dept)
            cur.execute(stmt, args)
            res = cur.fetchone()[0]
            cur.close()
            return res
        
     
    def removeuser(self, name):  ##shift record to deleted table
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
        
    def close(self): ##close connection to db after use
        self.conn.close()
        
    def checkpin(self, user, pin): ##check pin for chging pin
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
        
    def checkleavedays(self, user):  ##return user remaining leave float
        cur = self.conn.cursor()
        stmt = "SELECT remaining FROM mydb WHERE user = ?"
        args = (user, )
        cur.execute(stmt, args)
        res = cur.fetchone()[0]
        cur.close()
        return float(res)
        
    def genleaveid(self, user, start, days): ##return unique leaveid
        return user[:3] + start + user[-3:] + days
        
    def applyleave(self, user, start, end, days, reason): ##add to apply_user table
        remaining = self.checkleavedays(user)
        if remaining >= float(days):
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
        
    def findsuper(self, dept):  #return chat id of admin of dept
        cur = self.conn.cursor()
        stmt = "SELECT chatid FROM mydb WHERE dept = ? AND admin = 'Yes'"
        args = (dept, )
        cur.execute(stmt, args)
        res = cur.fetchone()[0]
        cur.close()
        return res
        
    def findchatid(self, user):  #return chat id of user
        cur = self.conn.cursor()
        stmt = "SELECT chatid FROM mydb WHERE user = ?"
        args = (user, )
        cur.execute(stmt, args)
        res = cur.fetchone()[0]
        cur.close()
        return res
        
    def getdeptnames(self, dept):  ##return name of all in dept for admin check leave
        cur = self.conn.cursor()
        stmt = "SELECT user FROM mydb WHERE dept = ?"
        args = (dept, )
        cur.execute(stmt, args)
        res = []
        for rows in cur.fetchall():
            res.append(rows[0])
        cur.close()
        return res
        
    def getapprovedleaves(self, user): ##return list of all users approved ##each leave is a tuple
        cur = self.conn.cursor()
        stmt = "SELECT * FROM approve_" + user
        cur.execute(stmt)
        res = cur.fetchall()
        cur.close()
        return res
        
    def getappliedleaves(self, user): ##return list of all users applied ##each leave is a tuple
        cur = self.conn.cursor()
        stmt = "SELECT * FROM apply_" + user
        cur.execute(stmt)
        res = cur.fetchall()
        cur.close()
        return res
        
    def getrejectedleaves(self, user):  ##return list of all users rejected ##each leave is a tuple
        cur = self.conn.cursor()
        stmt = "SELECT * FROM reject_" + user
        cur.execute(stmt)
        res = cur.fetchall()
        cur.close()
        return res
        
    def seeappliedleave(self, user, id): ##return leave detail in tuple
        cur = self.conn.cursor()
        stmt = "SELECT * FROM apply_" + user + " WHERE id = ?"
        args = (id, )
        cur.execute(stmt, args)
        res = cur.fetchone()
        cur.close()
        return res
        
    def seeapprovedleave(self, user, id):  ##return leave detail in tuple
        cur = self.conn.cursor()
        stmt = "SELECT * FROM approve_" + user + " WHERE id = ?"
        args = (id, )
        cur.execute(stmt, args)
        res = cur.fetchone()
        cur.close()
        return res
        
    def approveleave(self, user, id):  #shift to approve_ table, deduct leave return True if succesful
        cur = self.conn.cursor()
        stmt = "SELECT days FROM apply_" + user + " WHERE id = ?"
        args = (id, )
        cur.execute(stmt, args)
        remaining = self.checkleavedays(user) - float(cur.fetchone()[0])
        if remaining < 0:
            cur.close()
            return False
        stmt = "UPDATE mydb SET remaining = ? WHERE user = ?"
        args2 = (str(remaining), user)
        cur.execute(stmt, args2)
        stmt = "INSERT INTO approve_" + user + " SELECT * FROM apply_" + user + " WHERE id = ?"
        cur.execute(stmt, args)
        stmt = "DELETE FROM apply_" + user + " WHERE id = ?"
        cur.execute(stmt, args)
        self.conn.commit()
        cur.close()
        return True
        
    
    def rejectleave(self, user, id, reason):  #shift to reject_ table add reason
        cur = self.conn.cursor()
        stmt = "INSERT INTO reject_" + user + " SELECT * FROM apply_" + user + " WHERE id = ?"
        args = (id, )
        cur.execute(stmt, args)
        stmt = "DELETE FROM apply_" + user + " WHERE id = ?"
        cur.execute(stmt, args)
        stmt = "UPDATE reject_" + user + " SET reason = ? WHERE id = ?"
        args = (reason, id)
        cur.execute(stmt, args)
        self.conn.commit()
        cur.close()
        
        
    def cancelleave(self, user, id, table):
        cur = self.conn.cursor()
        if table == "approve_":
            stmt = "SELECT start,days FROM approve_" + user + " WHERE id = ?"
            args = (id, )
            cur.execute(stmt, args)
            res = cur.fetchone()
            start = datetime.datetime.strptime(res[0][:10], '%d/%m/%Y')
            if datetime.datetime.now() < start: #check leave havent started or ended  ##add leavedays back to remaining
                stmt = "SELECT remaining FROM mydb WHERE user = ?"
                args = (user, )
                cur.execute(stmt, args)
                remaining = float(res[1]) + float(cur.fetchone()[0])
                stmt = "UPDATE mydb SET remaining = ? WHERE user = ?"
                args = (str(remaining), user)
                cur.execute(stmt, args)
            else:
                cur.close()
                return False
        stmt = "DELETE FROM " + table + user + " WHERE id = ?"
        args = (id, )
        cur.execute(stmt, args)
        self.conn.commit()
        cur.close()
        return True
        
    def removeleave(self, user, id, table): #use to clearhistory
        cur = self.conn.cursor()
        stmt = "DELETE FROM " + table + user + " WHERE id = ?"
        args = (id, )
        cur.execute(stmt, args)
        self.conn.commit()
        cur.close()
        
    def clearhistory(self, date):
        cur = self.conn.cursor()
        stmt = "SELECT user FROM mydb WHERE dept != admin"
        cur.execute(stmt)
        res = cur.fetchall()
        for user in res:
            name = user[0]
            approve = self.getappliedleaves(name)
            for leave in approve:
                if datetime.datetime.strptime(leave[2][:10], '%d/%m/%Y') < date: 
                    self.removeleave(name, leave[0], "approve_")
                    
            reject = self.getrejectedleaves(name)
            for leave in reject: #all leave in reject rmv
                self.removeleave(name, leave[0], "reject_")
                    
            apply = self.getappliedleaves(name)
            for leave in apply:
                if datetime.datetime.strptime(leave[2][:10], '%d/%m/%Y') < date:
                    self.removeleave(name, leave[0], "apply_")
                    
        self.conn.commit()
        cur.close()
        
def main():
    db = DBHelper()
    res = db.test()
    db.close()


if __name__ == '__main__':
    main()


