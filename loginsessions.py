import datetime

from telegram import InlineKeyboardButton

from sessions import *
from dbhelper import DBHelper

pinlength = 4 ##length of pin

class Userloginsession(TextSession):  #wait for username input
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = None
        self.reply = "Enter Username"
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        self.user = data
        return retval(Pinloginsession(self))
            
class Pinloginsession(ButtonSession):  #wait for pin input
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = pin_keyboard
        self.reply = "Enter Pin (4 more num)"
        self.passwd = ""
        
    def userlogin(self):
        db = DBHelper()
        res = db.login(self.user, self.passwd, self.chat_id)
        db.close()
        self.passwd = ""
        if not res:
            self.user = ""
            return False
        else:
            self.login = True
            self.dept = res[1]
            if res[0] == "Yes":
                self.admin = True
            return True
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "Cancel":  ##reset pin input
            self.passwd = ""
            length = pinlength
        else:   ##length = remaining num
            self.passwd = self.passwd + data
            length = pinlength - len(self.passwd)
        if length <= 0:
            if self.userlogin():
                return retval(self, "")
            else:
                return retval(Tryloginsession(self, "Incorrect username/password, Try again?"))
                    
        else:  ##update to show remaining numbers to press
            self.reply = "Enter Pin (" + str(length) + " more num)"
            return retval(self)
            
class Tryloginsession(ButtonSession):   #try login or retry login
    def __init__(self, chatsession, reply):
        super().__init__(session=chatsession)
        self.keyboard = [[InlineKeyboardButton('Yes', callback_data='Yes'), InlineKeyboardButton('No', callback_data='No')]]
        self.reply = reply
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "Yes":
            return retval(Userloginsession(self))
        else:
            return retval(None, "Bye Bye")








