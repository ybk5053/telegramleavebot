import datetime

from telegram import InlineKeyboardButton

from sessions import *
from dbhelper import DBHelper


pin_keyboard = [[InlineKeyboardButton('1', callback_data='1'), InlineKeyboardButton('2', callback_data='2'), InlineKeyboardButton('3', callback_data='3')],
        [InlineKeyboardButton('4', callback_data='4'), InlineKeyboardButton('5', callback_data='5'), InlineKeyboardButton('6', callback_data='6')],
        [InlineKeyboardButton('7', callback_data='7'), InlineKeyboardButton('8', callback_data='8'), InlineKeyboardButton('9', callback_data='9')],
        [InlineKeyboardButton('Cancel', callback_data='Cancel')]]

yesno_keyboard = [[InlineKeyboardButton('Yes', callback_data='Yes'), InlineKeyboardButton('No', callback_data='No')]]

class LoginSession(Session):
    def __init__(self, session=None):
        super().__init__(session=session)
        self.passwd = session.passwd

class Userloginsession(LoginSession):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = None
        self.reply = "Enter Username"
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        self.user = data
        return retval(Pinloginsession(self))
            
class Pinloginsession(LoginSession):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.keyboard = pin_keyboard
        self.reply = "Enter Pin (4 more num)"
        
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
        super().handle(time, lastmessageid)
        if data == "Cancel":
            self.passwd = ""
            length = 4
        else:
            self.passwd = self.passwd + data
            length = 4 - len(self.passwd)
        if length <= 0:
            if self.userlogin():
                return retval(self, "")
            else:
                return retval(Tryloginsession(self, "Incorrect username/password, Try again?"))
                    
        else:
            self.reply = "Enter Pin (" + str(length) + " more num)"
            return retval(self)
            
class Tryloginsession(LoginSession):
    def __init__(self, chatsession, reply):
        super().__init__(session=chatsession)
        self.keyboard = yesno_keyboard
        self.reply = reply
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if data == "Yes":
            return retval(Userloginsession(self))
        else:
            return retval(None, "Bye Bye")

            
            
            
def main():
    s = Session(123, datetime.datetime.now())
    s2 = Session(124, datetime.datetime.now(), session=s)
    print(s2.chat_id)
    print(s2.wait)

if __name__ == '__main__':
    main()






