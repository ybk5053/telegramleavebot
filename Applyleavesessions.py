import datetime

from telegramcalendar import create_calendar

from dbhelper import DBHelper
from sessions import *

#todo at confirm button for calendar

class Waitdatesession(ButtonSession): #contains calendar keyboard
    def __init__(self, chatsession, showndate, start, blockdate=None):
        super().__init__(session=chatsession)
        self.showndate = showndate
        if blockdate is None:
            self.blockdate = datetime.datetime.now()
        else:
            self.blockdate = blockdate
        self.keyboard = self.calendar(showndate, start)
        
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
        
        
    def calendar(self, time, start):
        return create_calendar(time.year, time.month, self.blockdate, start)
        
    def datetostring(self, date, am):
        months_name = ['blank', ' January ', ' Febuary ', ' March ', ' April ', ' May ', ' June ', ' July ', ' August ', ' September ', ' October ', ' November ', ' December ']
        day = str(date.day)
        month = months_name[date.month]
        year = str(date.year)
        if len(day) < 2:
            day = "0" + day
        return day + month + year + " " + am
            
class Applystartdatesession(Waitdatesession): #wait for start date selection
    def __init__(self, chatsession, showndate):
        super().__init__(chatsession=chatsession,showndate=showndate,start=True)
        self.startam = "am"
        self.reply = self.newreply()
        
    def newreply(self):
        return "Leave starting on: " + self.datetostring(self.showndate, self.startam) + "\nConfirm to confirm starting date"
        
    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "next-month":
            self.showndate = self.next_month()
            self.keyboard = self.calendar(self.showndate, True)
            self.reply = self.newreply()
            return retval(self)
        elif data == "previous-month":
            self.showndate = self.previous_month()
            self.keyboard = self.calendar(self.showndate, True)
            self.reply = self.newreply()
            return retval(self)
        elif data[0:13] == "calendar-day-":
            self.showndate = self.get_day(data)
            self.reply = self.newreply()
            return retval(self)
        elif data == "am" or data == "pm":
            self.startam = data
            self.reply = self.newreply()
            return retval(self)
        elif data == "Confirm":
            self.leavestart = self.showndate
            return retval(Applyenddatesession(self, self.showndate))
        elif data == "ignore":
            return retval(self)

class Applyenddatesession(Waitdatesession): #wait for end date selection
    def __init__(self, chatsession, showndate):
        super().__init__(chatsession=chatsession,showndate=showndate,start=False,blockdate=showndate)
        self.leavestart = chatsession.leavestart
        self.startam = chatsession.startam
        self.endam = "night"
        self.reply = self.newreply()
        
    def newreply(self):
        print(self.startam)
        return "Leave starting on: " + self.datetostring(self.leavestart, self.startam) + "\nLeave ending on: " + self.datetostring(self.showndate, self.endam) + "\nConfirm to confirm ending date"

    def handle(self, data, time, lastmessageid):
        super().handle(data, time, lastmessageid)
        if data == "next-month":
            self.showndate = self.next_month()
            self.keyboard = self.calendar(self.showndate, True)
            self.reply = self.newreply()
            return retval(self)
        elif data == "previous-month":
            self.showndate = self.previous_month()
            self.keyboard = self.calendar(self.showndate, True)
            self.reply = self.newreply()
            return retval(self)
        elif data[0:13] == "calendar-day-":
            self.showndate = self.get_day(data)
            self.reply = self.newreply()
            return retval(self)
        elif data == "pm" or data == "eve":
            self.endam = data
            self.reply = self.newreply()
            return retval(self)
        elif data == "Confirm":
            self.leaveend = self.showndate
            return retval(Applyreasonsession(self))
        elif data == "ignore":
            return retval(self)
       
class Applyreasonsession(TextSession): #enter a reason for leave
    def __init__(self, chatsession):
        super().__init__(session=chatsession)
        self.leavestart = chatsession.leavestart
        self.startam = chatsession.startam
        self.leaveend = chatsession.leaveend
        self.endam = chatsession.endam
        self.reply = "Leave starting on: " + self.datetostring(self.leavestart, self.startam) + "\nLeave ending on: " + self.datetostring(self.leaveend, self.endam) + "\nEnter reason for leave?"
        
    def datetostring(self, date, am):
        months_name = ['blank', ' January ', ' Febuary ', ' March ', ' April ', ' May ', ' June ', ' July ', ' August ', ' September ', ' October ', ' November ', ' December ']
        day = str(date.day)
        month = months_name[date.month]
        year = str(date.year)
        if len(day) < 2:
            day = "0" + day
        return day + month + year + " " + am
        
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
        if db.applyleave(self.user, self.leavestart.strftime('%d/%m/%Y') + " " + self.startam, self.leaveend.strftime('%d/%m/%Y') + " " + self.endam, str(leavedays), self.leavereason):
            #datetime.strptime(date, '%m/%d/%Y') for string to date
            return True
        else:
            return False
        
    def checkleavedays(self):
        delta = (self.leaveend - self.leavestart).days + 1
        wkday = self.leavestart.weekday()
        days = 0.0
        for x in range(0, delta):
            if wkday < 5:
                days += 1
            wkday += 1
            if wkday > 6:
                wkday = 0
        if self.startam == "pm":
            days = days - 0.5
        if self.endam == "pm":
            days = days - 0.5
        return days
                
def main():
    num = "10"
    num2 = float(num)
    num3 = num2 + 0.5
    #str = "{:.1f}".format(num)
    print(num3)
    print(num)
    print(num2)
    
    
if __name__ == '__main__':
    main()






