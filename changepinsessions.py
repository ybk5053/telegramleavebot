import datetime

from telegram import InlineKeyboardButton

from dbhelper import DBHelper
from sessions import *


pin_keyboard = [[InlineKeyboardButton('1', callback_data='1'), InlineKeyboardButton('2', callback_data='2'), InlineKeyboardButton('3', callback_data='3')],
        [InlineKeyboardButton('4', callback_data='4'), InlineKeyboardButton('5', callback_data='5'), InlineKeyboardButton('6', callback_data='6')],
        [InlineKeyboardButton('7', callback_data='7'), InlineKeyboardButton('8', callback_data='8'), InlineKeyboardButton('9', callback_data='9')],
        [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
        
class Checkpinsession(Session):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = pin_keyboard
        self.reply = "Enter current pin (4 more num)"
        
    def checkpin(self):
        db = DBHelper()
        res = db.checkpin(self.user, self.passwd)
        db.close()
        return res
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
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
          
class Newpinsession(Session):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = pin_keyboard
        self.reply = "Enter new Pin (4 more num)"
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
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
            
class Checknewpinsession(Session):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = pin_keyboard
        self.reply = "Reenter new pin (4 more num)"
        self.passwd = chatsession.passwd
        
    def checkpin(self):
        if self.passwd == self.newpasswd:
            db = DBHelper()
            res = db.updatepin(self.user, self.passwd)
            db.close()
            return True
        else:
            return False
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
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
            
            

def main():
    s = Session(123, datetime.datetime.now())
    s2 = Session(124, datetime.datetime.now(), session=s)
    print(s2.chat_id)
    print(s2.wait)

if __name__ == '__main__':
    main()






