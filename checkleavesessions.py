import datetime

from telegram import InlineKeyboardButton

from telegramcalendar import create_calendar

from dbhelper import DBHelper

app_keyboard = [[InlineKeyboardButton('See Applied Leaves', callback_data='Applied'), InlineKeyboardButton('See Approved Leaves', callback_data='Approved')]]
approvedaction_keyboard = [[InlineKeyboardButton('Cancel', callback_data='Cancel'), InlineKeyboardButton('Back', callback_data='Back')]]
appliedaction_keyboard = [[InlineKeyboardButton('Change', callback_data='Change'), InlineKeyboardButton('Back', callback_data='Back')]]
adminappliedaction_keyboard = [[InlineKeyboardButton('Approve', callback_data='Approve'), InlineKeyboardButton('Reject', callback_data='Reject'), InlineKeyboardButton('Back', callback_data='Back')]]

class Seeothersession(Session):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        db = DBHelper()
        res = db.getdeptnames()
        db.close()
        buttons = []
        for names in res:
            buttons.append(InlineKeyboardButton(names[0], callback_data=names[0]))
        self.keyboard = buttons
        self.reply = "Select user to view"
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        db = DBHelper()
        res = db.findnameinstance(data, self.dept):
        db.close()
        if res:
            return retval(Seeleavesession(self, data))
            
        
        
class Seeleavesession(Session):
    def __init__(self, chatsession, user):
        super().__init__(session=chatsession)
        self.checkleave = user
        self.keyboard = app_keyboard
        self.reply = "Approved or Applied"
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if data == "Approved":
            return retval(Seeapprovedsession(self))
        elif data == "Applied":
            retun retval(Seeappliedsession(self))
            
            
class Seeapprovedsession(Session):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.checkleave = chatsession.checkleave
        db = DBHelper()
        res = db.getapprovedleaves(self.checkleave)
        db.close()
        self.leaveids = []
        for names in res:
            buttons.append([InlineKeyboardButton(names[1] + " - " + names[2] + ": " + names[3], callback_data=names[0])])
            self.leaveids.append(names[0])
        buttons.append(InlineKeyboardButton('Back', callback_data='Back')
        self.keyboard = buttons
        self.reply = "Which one"
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if data in self.leaveids:
            return retval(Waitapprovedactionsession(self, data))
            
            
class Seeappliedsession(Session):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.checkleave = chatsession.checkleave
        db = DBHelper()
        res = db.getappliedleaves(self.checkleave)
        db.close()
        self.leaveids = []
        for names in res:
            buttons.append([InlineKeyboardButton(names[1] + " - " + names[2] + ": " + names[3], callback_data=names[0])])
            self.leaveids.append(names[0])
        buttons.append(InlineKeyboardButton('Back', callback_data='Back')
        self.keyboard = buttons
        self.reply = "Which one"
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if data in self.leaveids:
            return retval(Waitappliedactionsession(self, data))
            
class Waitappliedactionsession(Session):
    def __init__(self, chatsession, leaveid):
        super().__init__(session=chatsession)
        self.checkleave = chatsession.checkleave
        self.leaveid = leaveid
        db = DBHelper()
        res = db.getappliedleaves(self.checkleave, self.leaveid)
        db.close()
        if self.admin:
            self.keyboard = adminappliedaction_keyboard
        else:
            self.keyboard = appliedaction_keyboard
        self.reply = "Leave from: " + res[0] + "to" + res[1] + "\nReason: " + res[2]
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if data == "Back":
            return retval(Waitappliedactionsession(self, data))
            
class Waitapprovedactionsession(Session):
    def __init__(self, chatsession, leaveid):
        super().__init__(session=chatsession)
        self.checkleave = chatsession.checkleave
        self.leaveid = leaveid
        db = DBHelper()
        res = db.getappliedleaves(self.checkleave, self.leaveid)
        db.close()
        for names in res:
            buttons.append(InlineKeyboardButton(names[1] + " - " + names[2] + ": " + names[3], callback_data=names[0]))
            self.leaveids.append(names[0])
        buttons.append(InlineKeyboardButton('Back', callback_data='Back')
        self.keyboard = buttons
        self.reply = "Which one"
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if data in self.leaveids:
            return retval(Waitappliedactionsession(self, data))
            
                
def main():
    s = Session(123, datetime.datetime.now())
    s2 = Session(124, datetime.datetime.now(), session=s)
    print(s2.chat_id)
    print(s2.wait)

if __name__ == '__main__':
    main()






