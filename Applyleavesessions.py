import datetime

from dbhelper import DBHelper
from sessions import *


            
class Applystartdatesession(Waitdatesession):
    def __init__(self, chatsession, showndate):
        super().__init__(chatsession=chatsession,showndate=showndate)
        self.reply = "Select leave starting date"
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if data == "next-month":
            return retval(Applystartdatesession(self, self.next_month()))
        elif data == " previous-month":
            return retval(Applystartdatesession(self, self.previous_month()))
        elif data[0:13] == "calendar-day-":
            self.showndate = self.get_day(data)
            self.leavestart = self.showndate
            return retval(Applyenddatesession(self, self.showndate))
        elif data == "ignore":
            return retval(self)

class Applyenddatesession(Waitdatesession):
    def __init__(self, chatsession, showndate):
        super().__init__(chatsession=chatsession,showndate=showndate,blockdate=showndate)
        self.reply = "Leave starting on: " + self.datetostring(self.leavestart) + "\nEnter leave ending date"

    def datetostring(self, date):
        months_name = ['blank', ' January ', ' Febuary ', ' March ', ' April ', ' May ', ' June ', ' July ', ' August ', ' September ', ' October ', ' November ', ' December ']
        day = str(date.day)
        month = months_name[date.month]
        year = str(date.year)
        if len(day) < 2:
            day = "0" + day
        return day + month + year
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        if data == "next-month":
            return retval(Applyenddatesession(self, self.next_month()))
        elif data == " previous-month":
            return retval(Applyenddatesession(self, self.previous_month()))
        elif data[0:13] == "calendar-day-":
            self.showndate = self.get_day(data)
            self.leaveend = self.showndate
            return retval(Applyreasonsession(self))
        elif data == "ignore":
            return retval(self)
       
class Applyreasonsession(Session):
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.leavestart = chatsession.leavestart
        self.leaveend = chatsession.leaveend
        self.reply = "Leave starting on: " + self.datetostring(self.leavestart) + "\nLeave ending on: " + self.datetostring(self.leaveend) + "\nWhat is your reason for leave?"
        
    def datetostring(self, date):
        months_name = ['blank', ' January ', ' Febuary ', ' March ', ' April ', ' May ', ' June ', ' July ', ' August ', ' September ', ' October ', ' November ', ' December ']
        day = str(date.day)
        month = months_name[date.month]
        year = str(date.year)
        if len(day) < 2:
            day = "0" + day
        return day + month + year
        
    def handle(self, data, time, lastmessageid):
        super().handle(time, lastmessageid)
        self.leavereason = data
        if self.applyleave():
            return retval(self, "Leave application send to supervisor")
        else:
            return retval(self, "You don't have enough leaves left")
            
    def applyleave(self):
        leavedays = self.checkleavedays()
        db = DBHelper()
        if db.applyleave(self.user, self.leavestart.strftime('%m/%d/%Y'), self.leaveend.strftime('%m/%d/%Y'), str(leavedays), self.leavereason):
            #datetime.strptime(date, '%m/%d/%Y') for string to date
            return True
        else:
            return False
        
    def checkleavedays(self):
        delta = (self.leaveend - self.leavestart).days + 1
        print(delta)
        wkday = self.leavestart.weekday()
        days = 0
        for x in range(0, delta):
            if wkday < 5:
                days += 1
            wkday += 1
            if wkday > 6:
                wkday = 0
        return days
                
def main():
    print(datetime.datetime.now())
    s = Session(123, datetime.datetime.now())
    s2 = Applystartdatesession(s, datetime.datetime.now())
    s3 = s2.handle("calendar-day-13", datetime.datetime.now(),123).session
    res = s3.handle("calendar-day-15", datetime.datetime.now(),123).session
    print(res.reply)
    res2 = res.handle("calendar-day-15", datetime.datetime.now(),123)
    print(res2.reply)

if __name__ == '__main__':
    main()






