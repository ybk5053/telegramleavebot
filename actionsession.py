import datetime

from telegram import InlineKeyboardButton

from dbhelper import DBHelper
from sessions import *
from changepinsessions import Checkpinsession
from addremovesessions import Addusersession, Removeusersession
from Applyleavesessions import Applystartdatesession
from checkleavesessions import Seeleavesession, Seeothersession

admin_keyboard = [[InlineKeyboardButton('Apply Leave', callback_data='Apply'), InlineKeyboardButton('Check Leaves', callback_data='Check')], 
        [InlineKeyboardButton('Add User', callback_data='Add'), InlineKeyboardButton('Remove User', callback_data='Remove')], 
        [InlineKeyboardButton('Change Pin', callback_data='Change Pin'), InlineKeyboardButton('Logout', callback_data='Logout')]]
        
action_keyboard = [[InlineKeyboardButton('Apply Leave', callback_data='Apply'), InlineKeyboardButton('Check My Leaves', callback_data='Check')],
        [InlineKeyboardButton('Change Pin', callback_data='Change Pin'), InlineKeyboardButton('Logout', callback_data='Logout')]]
            
class Waitactionsession(ButtonSession):  #main screen for bot after login
    def __init__(self, chatsession, reply=None):
        super().__init__(session=chatsession)
        if self.admin:
            self.keyboard = admin_keyboard
        else:
            self.keyboard = action_keyboard
        if reply is None:
            self.reply = "Welcome " + self.user + "\nWhat do you want to do?"
        else:
            self.reply = reply + "\nWelcome " + self.user + "\nWhat do you want to do?"
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "Apply":
            return retval(Applystartdatesession(self, datetime.datetime.now()))
        elif data == "Check":
            if self.admin:
                return retval(Seeothersession(self))
            else:
                return retval(Seeleavesession(self, self.user))
        elif data == "Add":
            if self.admin:
                return retval(Addusersession(self))
            else:
                return retval(Waitactionsession(self, "Sorry you are not a admin"))
        elif data == "Remove":
            if self.admin:
                return retval(Removeusersession(self))
            else:
                return retval(Waitactionsession(self, "Sorry you are not a admin"))
        elif data == "Change Pin":
            return retval(Checkpinsession(self))
        elif data == "Logout":
            return retval(None, "Bye Bye")
            







