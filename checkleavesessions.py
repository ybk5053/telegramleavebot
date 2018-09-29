import datetime

from telegram import InlineKeyboardButton

from telegramcalendar import create_calendar

from dbhelper import DBHelper
from sessions import *

app_keyboard = [[InlineKeyboardButton('See Applied Leaves', callback_data='Applied')], [InlineKeyboardButton('See Approved Leaves', callback_data='Approved')], [InlineKeyboardButton('See Rejected Leaves', callback_data='Rejected')]]

approvedaction_keyboard = [[InlineKeyboardButton('Cancel', callback_data='Cancel'), InlineKeyboardButton('Back', callback_data='Back')]]

viewonly_keyboard = [[InlineKeyboardButton('Back', callback_data='Back')]]

appliedaction_keyboard = [[InlineKeyboardButton('Cancel', callback_data='Cancel'), InlineKeyboardButton('Back', callback_data='Back')]]

adminappliedaction_keyboard = [[InlineKeyboardButton('Approve', callback_data='Approve'), InlineKeyboardButton('Reject', callback_data='Reject'), InlineKeyboardButton('Back', callback_data='Back')]]


class Seeothersession(ButtonSession):  #if admin, select which users leave to view
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        db = DBHelper()
        res = db.getdeptnames(self.dept)
        db.close()
        buttons = []
        for names in res: #add names to buttons
            if names == self.user:
                buttons.append([InlineKeyboardButton('Myself', callback_data=names)])
            else:
                buttons.append([InlineKeyboardButton(names, callback_data=names)])
        self.keyboard = buttons
        self.reply = "Select user to view"
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        db = DBHelper()
        res = db.findnameinstance(data, self.dept)
        db.close()
        if res:
            return retval(Seeleavesession(self, data))
            
class Seeleavesession(ButtonSession): #choose to view accepted, pending or rejected leaves
    def __init__(self, chatsession, user):
        super().__init__(session=chatsession)
        self.checkleave = user #name of user which leave being viewed
        db = DBHelper()
        left = str(db.checkleavedays(user))
        db.close()
        self.keyboard = app_keyboard
        self.reply = user + " has " + left + " leaves remaining"
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "Approved":
            return retval(Seeapprovedsession(self))
        elif data == "Applied":
            return retval(Seeappliedsession(self))
        elif data == "Rejected":
            return retval(Seerejectedsession(self))
            
class Seeapprovedsession(ButtonSession): #see list of all approved for checkuser
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.checkleave = chatsession.checkleave
        db = DBHelper()
        res = db.getapprovedleaves(self.checkleave)
        left = str(db.checkleavedays(self.user))
        db.close()
        self.leaveids = []
        buttons = []
        for leaves in res: ##add inline button for each leave
            buttons.append([InlineKeyboardButton(leaves[1] + " - " + leaves[2] + ": " + leaves[4], callback_data=leaves[0])])
            self.leaveids.append(leaves[0])
        buttons.append([InlineKeyboardButton('Back', callback_data='Back')])
        self.keyboard = buttons
        self.reply = self.user + " has " + left + " leaves remaining"
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data in self.leaveids:
            return retval(Waitapprovedactionsession(self, data))
        elif data == "Back":
            return retval(Seeleavesession(self, self.checkleave))
            
class Seeappliedsession(ButtonSession):  #see list of all applied for checkuser
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.checkleave = chatsession.checkleave
        db = DBHelper()
        res = db.getappliedleaves(self.checkleave)
        left = str(db.checkleavedays(self.user))
        db.close()
        self.leaveids = []
        buttons = []
        for leaves in res:
            buttons.append([InlineKeyboardButton(leaves[1] + " - " + leaves[2] + ": " + leaves[4], callback_data=leaves[0])])
            self.leaveids.append(leaves[0])
        buttons.append([InlineKeyboardButton('Back', callback_data='Back')])
        self.keyboard = buttons
        self.reply = self.user + " has " + left + " leaves remaining"
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data in self.leaveids:
            return retval(Waitappliedactionsession(self, data))
        elif data == "Back":
            return retval(Seeleavesession(self, self.checkleave))
            
class Seerejectedsession(ButtonSession):  #see list of all rejected for checkuser
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.checkleave = chatsession.checkleave
        db = DBHelper()
        res = db.getrejectedleaves(self.checkleave)
        left = str(db.checkleavedays(self.user))
        db.close()
        buttons = []
        for leaves in res:
            buttons.append([InlineKeyboardButton(leaves[1] + " - " + leaves[2] + ": " + leaves[4], callback_data="ignore")])
        buttons.append([InlineKeyboardButton('Back', callback_data='Back')])
        self.keyboard = buttons
        self.reply = self.user + " has " + left + " leaves remaining"
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "ignore":
            return retval(self)
        elif data == "Back":
            return retval(Seeleavesession(self, self.checkleave))
            
class Waitappliedactionsession(ButtonSession):  #view, cancel(own leaves only), approve(admin), reject(admin) leaves
    def __init__(self, chatsession, leaveid):
        super().__init__(session=chatsession)
        self.checkleave = chatsession.checkleave
        self.leaveid = leaveid  ##id of current viewing leave
        db = DBHelper()
        res = db.seeappliedleave(self.checkleave, self.leaveid)
        db.close()
        if self.admin:
            self.keyboard = adminappliedaction_keyboard
        else:
            self.keyboard = appliedaction_keyboard
        self.reply = "Leave from: " + res[1] + " to " + res[2] + " : " + res[3] + " days\nReason: " + res[4]
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "Back":
            return retval(Seeappliedsession(self))
        elif data == "Cancel":
            db = DBHelper()
            db.cancelleave(self.checkleave, self.leaveid, "apply_")
            db.close()
            return retval(self, "Leave Application canceled")
        elif data == "Approve":
            if self.admin:
                db = DBHelper()
                res = db.approveleave(self.checkleave, self.leaveid)
                if res:
                    db.close()
                    return retval(self, "Leave approved")
                else:  #reject leave cos not enough remaining
                    db.rejectleave(self.checkleave, self.leaveid, "Not enough leaves")
                    db.close()
                    return retval(self, "Leave rejected")
        elif data == "Reject":
            if self.admin:
                return retval(Waitrejectleavereasonsession(self))
                
class Waitrejectleavereasonsession(TextSession): #view only
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.checkleave = chatsession.checkleave
        self.leaveid = chatsession.leaveid
        self.reply = "Enter reason for reject leave"
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if self.admin:
            db = DBHelper()
            db.rejectleave(self.checkleave, self.leaveid, data)
            db.close()
            return retval(self, "Leave rejected")

class Waitapprovedactionsession(ButtonSession): #view, cancel(own leaves only)
    def __init__(self, chatsession, leaveid):
        super().__init__(session=chatsession)
        self.checkleave = chatsession.checkleave
        self.leaveid = leaveid
        db = DBHelper()
        res = db.seeapprovedleave(self.checkleave, self.leaveid)
        db.close()
        if self.user == self.checkleave:
            self.keyboard = approvedaction_keyboard
        else:
            self.keyboard = viewonly_keyboard
        self.reply = "Leave from: " + res[1] + " to " + res[2] + " : " + res[3] + " days\nReason: " + res[4]
        
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "Back":
            return retval(Seeapprovedsession(self))
        elif data == "Cancel":
            if self.user == self.checkleave:
                db = DBHelper()
                res = db.seeapprovedleave(self.checkleave, self.leaveid)
                res2 = db.cancelleave(self.checkleave, self.leaveid, "approve_")
                db.close()
                if res2:
                    return retval(self, "Approved Leave from: " + res[1] + "to" + res[2] + " canceled")
                else:
                    return retval(self, "Leave already started/over")
                

def main():
    print(datetime.datetime.now())
    s = Session(123, datetime.datetime.now())
    s2 = Seeothersession(s)
    s2.dept = "dept1"
    res = s2.handle("Asd", datetime.datetime.now(),123)
    print(res.session)
    

if __name__ == '__main__':
    main()





