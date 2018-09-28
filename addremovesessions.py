import datetime

from telegram import InlineKeyboardButton

from dbhelper import DBHelper
from sessions import *


default_pass = "1234" ##default 4 digit pin for new user
        
        
class Addusersession(TextSession):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.reply = "Create Username"
        
    def checknameexist(self, name):
        db = DBHelper()
        res = db.findnameinstance(name)
        db.close()
        return res
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if not self.checknameexist(data):
            self.adduser = data
            if self.dept == "admin":
                return retval(Waitdeptsession(self))
            else:
                self.adddept = self.dept
                return retval(Adminyesnosession(self))
        else:
            return retval(self, "Username already exist!")
        
class Removeusersession(TextSession):
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
        super().handle(data, time, lastmessageid)
        if self.remove(data):
            return retval(self, data + " have been removed.")
        else:
            return retval(self, data + " not found.")

class Adminyesnosession(ButtonSession):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = [[InlineKeyboardButton('Yes', callback_data='Yes'), InlineKeyboardButton('No', callback_data='No')]]
        self.reply = "Admin?"
        self.adduser = chatsession.adduser
        self.adddept = chatsession.adddept

    def createuser(self):
        if not self.admin:
            return False
        db = DBHelper()
        db.createuser(self.adduser, default_pass, self.adddept, self.addadmin)
        db.close()
        return True
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        self.addadmin = data
        if self.createuser():
            return retval(self, "New User Created.")
        else:
            return retval(self, "Failed Creating User.")
                
class Waitdeptsession(ButtonSession):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        db = DBHelper()
        res = db.getdepts()
        key = []
        self.keyboard = []
        x = 0
        i = 1
        for name in res:
            if x < 3:
                key.append(InlineKeyboardButton(name, callback_data=name))
            else:
                self.keyboard.append(key)
                key = [InlineKeyboardButton(name, callback_data=name)]
            if i == len(res):
                self.keyboard.append(key)
            x += 1
            i += 1
        self.reply = "Select department"
        self.adduser = chatsession.adduser
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        self.adddept = data
        return retval(Adminyesnosession(self))
            
            
           
   
   







