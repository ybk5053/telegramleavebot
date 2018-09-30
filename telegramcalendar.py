from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import calendar

def create_calendar(year,month,blockdate,start):
    markup = []
    #First row - Month and Year
    row=[]
    row.append(InlineKeyboardButton(calendar.month_name[month]+" "+str(year),callback_data="ignore"))
    if start:
        row.append(InlineKeyboardButton("AM",callback_data="am"))
        row.append(InlineKeyboardButton("PM",callback_data="pm"))
    else:
        row.append(InlineKeyboardButton("PM",callback_data="pm"))
        row.append(InlineKeyboardButton("Eve",callback_data="eve"))
    markup.append(row)
    #Second row - Week Days
    week_days=["M","T","W","R","F","S","U"]
    row=[]
    for day in week_days:
        row.append(InlineKeyboardButton(day,callback_data="ignore"))
    markup.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row=[]
        for day in week:
            if(day==0) or (blockdate.year==year and blockdate.month>month) or (blockdate.year==year and blockdate.month==month and day<blockdate.day) or (blockdate.year>year):
                row.append(InlineKeyboardButton(" ",callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(str(day),callback_data="calendar-day-"+str(day)))
        markup.append(row)
    #Last row - Buttons
    row=[]
    row.append(InlineKeyboardButton("<",callback_data="previous-month"))
    row.append(InlineKeyboardButton("Confirm",callback_data="Confirm"))
    row.append(InlineKeyboardButton(">",callback_data="next-month"))
    markup.append(row)
    return markup
