import datetime

from telegram import InlineKeyboardButton

from dbhelper import DBHelper


pin_keyboard = [[InlineKeyboardButton('1', callback_data='1'), InlineKeyboardButton('2', callback_data='2'), InlineKeyboardButton('3', callback_data='3')],
        [InlineKeyboardButton('4', callback_data='4'), InlineKeyboardButton('5', callback_data='5'), InlineKeyboardButton('6', callback_data='6')],
        [InlineKeyboardButton('7', callback_data='7'), InlineKeyboardButton('8', callback_data='8'), InlineKeyboardButton('9', callback_data='9')],
        [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
        
        

class retval: #return type for session.handle ##reply value used to get bot to do return to /start menu, send extra msg
    def __init__(self, session, reply=None):
        self.session = session
        self.reply = reply

class Session:  #base session class for session.handle
    
    #start, chat_id, login, user, passwd, dept, admin, lastmessageid
    #adduser, adddept, addadmin
    #

    def __init__(self, chatid=None, starttime=None, session=None):
        self.keyboard = None #inline keyboard to appear together with reply
        self.reply = "" #text to reply with
        if session is None:
            self.start = starttime  #timestamp for timeout
            self.chat_id = chatid  #chat id for session to talk to
            self.login = False #check if user is login
            self.user = "" #name of user
            self.dept = "" #dept of user
            self.admin = False #if user is admin
            self.lastmessageid = None #to edit last message incase timeout
        else:
            self.start = session.start 
            self.chat_id = session.chat_id
            self.login = session.login
            self.user = session.user
            self.dept = session.dept
            self.admin = session.admin
            self.lastmessageid = session.lastmessageid
            
    def timeout(self, time):  #timeout run by bot every 5 mins
        if (time-self.start).total_seconds() > 600:
            return (self.chat_id, self.lastmessageid)
            
    def handle(self, data, time, lastmessageid):  #handle message or button press
        self.lastmessageid = lastmessageid
        self.start = time
        
class ButtonSession(Session):   #for sessions with inlinekeyboard
    def handle(self, data, time, lastmessageid):  #handle message or button press
        super().handle(data, time, lastmessageid)
    
class TextSession(Session): #for sessions expect text reply
    def handle(self, data, time, lastmessageid):  #handle message or button press
        super().handle(data, time, lastmessageid)
    







