import datetime

from telegram import InlineKeyboardButton

from dbhelper import DBHelper
from sessions import *


        
class Checkpinsession(ButtonSession): #check old pin
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = pin_keyboard
        self.reply = "Enter current pin (4 more num)"
        self.passwd = ""
        
    def checkpin(self):
        db = DBHelper()
        res = db.checkpin(self.user, self.passwd)
        db.close()
        return res
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "Cancel":
            self.passwd = ""
            length = 4
        else:
            self.passwd = self.passwd + data
            length = 4 - len(self.passwd)
            
        if length <= 0:
            if self.checkpin():
                self.passwd = ""
                return retval(Newpinsession(self))
            else:
                self.passwd = ""
                return retval(self, "Wrong pin")
        else:
            self.reply = "Enter current pin (" + str(length) + " more num)"
            return retval(self)
          
class Newpinsession(ButtonSession): #enter new pin
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = pin_keyboard
        self.reply = "Enter new Pin (4 more num)"
        self.passwd = ""
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "Cancel":
            self.passwd = ""
            length = 4
        else:
            self.passwd = self.passwd + data
            length = 4 - len(self.passwd)
            
        if length <= 0:
            return retval(Checknewpinsession(self))
        else:
            self.reply = "Enter new pin (" + str(length) + " more num)"
            return retval(self)
            
class Checknewpinsession(ButtonSession): #double check new pin
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = pin_keyboard
        self.reply = "Reenter new pin (4 more num)"
        self.passwd = chatsession.passwd
        self.newpasswd = ""
        
    def checkpin(self):
        if self.passwd == self.newpasswd:
            db = DBHelper()
            res = db.updatepin(self.user, self.passwd)
            db.close()
            return True
        else:
            return False
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "Cancel":
            self.newpasswd = ""
            length = 4
        else:
            self.newpasswd = self.newpasswd + data
            length = 4 - len(self.newpasswd)
            
        if length <= 0:
            if self.checkpin():
                return retval(self, "Pin changed")
            else:
                return retval(self, "Wrong pin")
                    
        else:
            self.reply = "Reenter new pin (" + str(length) + " more num)"
            return retval(self)
            
            






