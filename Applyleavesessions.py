import datetime

from telegramcalendar import create_calendar

from dbhelper import DBHelper
from sessions import *

#todo at confirm button for calendar

class Waitdatesession(ButtonSession): #contains calendar keyboard
    def __init__(self, chatsession, showndate, blockdate=None):
        super().__init__(session=chatsession)
        self.showndate = showndate
        if blockdate is None:
            self.blockdate = datetime.datetime.now()
        else:
            self.blockdate = blockdate
        self.keyboard = self.calendar(showndate)
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
            
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
            
class Applystartdatesession(Waitdatesession): #wait for start date selection
    def __init__(self, chatsession, showndate):
        super().__init__(chatsession=chatsession,showndate=showndate)
        self.reply = "Select leave starting date"
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
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

class Applyenddatesession(Waitdatesession): #wait for end date selection
    def __init__(self, chatsession, showndate):
        super().__init__(chatsession=chatsession,showndate=showndate,blockdate=showndate)
        self.leavestart = chatsession.leavestart
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
        super().handle(data, time, lastmessageid)
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
       
class Applyreasonsession(TextSession): #enter a reason for leave
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
        super().handle(data, time, lastmessageid)
        self.leavereason = data
        if self.applyleave():
            return retval(self, "Leave application send to supervisor")
        else:
            return retval(self, "You don't have enough leaves left")
            
    def applyleave(self):
        leavedays = self.checkleavedays()
        db = DBHelper()
        if db.applyleave(self.user, self.leavestart.strftime('%d/%m/%Y'), self.leaveend.strftime('%d/%m/%Y'), str(leavedays), self.leavereason):
            #datetime.strptime(date, '%m/%d/%Y') for string to date
            return True
        else:
            return False
        
    def checkleavedays(self):
        delta = (self.leaveend - self.leavestart).days + 1
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
    d1 = datetime.datetime.strptime('10/10/2018', '%d/%m/%Y')
    d2 = datetime.datetime.strptime('13/10/2018', '%d/%m/%Y')
    print((d2 - d1).days)

if __name__ == '__main__':
    main()






