import datetime

from telegram import InlineKeyboardButton

from dbhelper import DBHelper
from sessions import *


pin_keyboard = [[InlineKeyboardButton('1', callback_data='1'), InlineKeyboardButton('2', callback_data='2'), InlineKeyboardButton('3', callback_data='3')],
        [InlineKeyboardButton('4', callback_data='4'), InlineKeyboardButton('5', callback_data='5'), InlineKeyboardButton('6', callback_data='6')],
        [InlineKeyboardButton('7', callback_data='7'), InlineKeyboardButton('8', callback_data='8'), InlineKeyboardButton('9', callback_data='9')],
        [InlineKeyboardButton('Cancel', callback_data='Cancel')]]

yesno_keyboard = [[InlineKeyboardButton('Yes', callback_data='Yes'), InlineKeyboardButton('No', callback_data='No')]]

dept_keyboard = [[InlineKeyboardButton('dept', callback_data='dept'), InlineKeyboardButton('dept2', callback_data='dept')]]
        
class AddRemoveSession(Session):
    def __init__(self, session):
        super().__init__(session=session)
        self.passwd = session.passwd
        self.adduser = session.adduser
        self.adddept = session.adddept
        self.addadmin = session.addadmin
        
class Addusersession(AddRemoveSession):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.reply = "Create Username"
        
    def checknameexist(self, name):
        db = DBHelper()
        res = db.findnameinstance(name)
        db.close()
        return res
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if not self.checknameexist(data):
            self.adduser = data
            return retval(Adminyesnosession(self))
        else:
            return retval(self, "Username already exist!")
        
class Removeusersession(AddRemoveSession):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.reply = "Enter Username to remove"
        
    def checknameexist(self, name):
        db = DBHelper()
        res = db.findnameinstance(name, self.dept)
        db.close()
        return res
        
    def remove(self, name):
        if self.checknameexist(name):
            db = DBHelper()
            db.removeuser(name)
            db.close()
            self.adduser = ""
            return True
        else:
            return False
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if self.remove(data):
            return retval(self, data + " have been removed.")
        else:
            return retval(self, data + " not found.")

class Createpinsession(AddRemoveSession):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = pin_keyboard
        self.reply = "Create a 4 digit pin"
        
    def createuser(self):
        if not self.admin:
            return False
        db = DBHelper()
        db.createuser(self.adduser, self.passwd, self.adddept, self.addadmin)
        db.close()
        self.adduser = ""
        self.passwd = ""
        self.adddept = ""
        self.addadmin = "No"
        return True
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if data == "Cancel":
            self.passwd = ""
            length = 4
        else:
            self.passwd = self.passwd + data
            length = 4 - len(self.passwd)
        if length <= 0:
                    
            if self.createuser():
                return retval(self, "New User Created.")
            else:
                return retval(self, "Failed Creating User.")
                    
                    
        else:
            self.reply = "Create a pin (" + str(length) + " more num)"
            return retval(self)
            
class Adminyesnosession(AddRemoveSession):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = yesno_keyboard
        self.reply = "Admin?"

        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        self.addadmin = data
        if self.dept == "admin":
            return retval(Waitdeptsession(self))
        else:
            self.adddept = self.dept
            return retval(Createpinsession(self))
                
class Waitdeptsession(AddRemoveSession):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = dept_keyboard
        self.reply = "Select department"
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        self.adddept = data
        return retval(Createpinsession(self))
            
            
           
   
   
                
def main():
    s = Session(123, datetime.datetime.now())
    s2 = Session(124, datetime.datetime.now(), session=s)
    print(s2.chat_id)
    print(s2.wait)

if __name__ == '__main__':
    main()






