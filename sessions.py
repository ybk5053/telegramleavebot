import datetime

from telegram import InlineKeyboardButton

from telegramcalendar import create_calendar

from dbhelper import DBHelper

class retval:
    def __init__(self, session, reply=None):
        self.session = session
        self.reply = reply

class Session:
    
    #start, chat_id, login, user, passwd, dept, admin, lastmessageid
    #adduser, adddept, addadmin
    #

    def __init__(self, chatid=None, starttime=None, session=None):
        self.keyboard = None
        self.leavestart = None
        self.leaveend = None
        self.newpasswd = ""
        self.adduser = ""
        self.adddept = ""
        self.addadmin = "No"
        self.passwd = ""
        if session is None:
            self.start = starttime
            self.chat_id = chatid
            self.login = False
            self.user = ""
            self.dept = ""
            self.admin = False
            self.lastmessageid = None
        else:
            self.start = session.start
            self.chat_id = session.chat_id
            self.login = session.login
            self.user = session.user
            self.dept = session.dept
            self.admin = session.admin
            self.lastmessageid = session.lastmessageid
            
    def timeout(self, time):
        if (time-self.start).total_seconds() < 600:
            return (self.chat_id, self.lastmessageid)
            
    def handle(self, time, lastmessageid):
        self.lastmessageid = lastmessageid
        self.start = time
        

            

class Waitdatesession(Session):
    def __init__(self, chatsession, showndate, blockdate=None):
        super().__init__(session=chatsession)
        self.leavestart = chatsession.leavestart
        self.leaveend = chatsession.leaveend
        self.showndate = showndate
        if blockdate is None:
            self.blockdate = datetime.datetime.now()
        else:
            self.blockdate = blockdate
        self.keyboard = self.calendar(showndate)
        
    def handle(self, time, lastmessageid):
        super().handle(time, lastmessageid)
            
    #data == 'next-month'
    def next_month(self):
        month = self.showndate.month
        year = self.showndate.year
        month+=1
        if month>12:
            month=1
            year+=1
        return self.showndate.replace(year=year,month=month)

    #data == 'previous-month'
    def previous_month(self):
        month = self.showndate.month
        year = self.showndate.year
        month-=1
        if month<1:
            month=12
            year-=1
        return self.showndate.replace(year=year,month=month)
            
    #call.data[0:13] == 'calendar-day-'
    def get_day(self, data):
        day=data[13:]
        date = datetime.datetime(int(self.showndate.year),int(self.showndate.month),int(day),0,0,0)
        return date
        
        
    def calendar(self, time):
        return create_calendar(time.year, time.month, self.blockdate)
        
        
        
        
                
def main():
    s = Session(123, datetime.datetime.now())
    s2 = Session(124, datetime.datetime.now(), session=s)
    print(s2.chat_id)
    print(s2.wait)

if __name__ == '__main__':
    main()






