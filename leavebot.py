import logging
import datetime

from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import JobQueue
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from dbhelper import DBHelper
from sessions import *
from actionsession import Waitactionsession
from loginsessions import Tryloginsession
import keys ##bot token

sessions = []

#todo change callback_query less predictable

#dbsetup.py for setup and clear history
#chg default pass for new user in addremovesessions.py
#chg pin length in loginsessions.py

token = keys.token
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

def checkforactivesession(id):
    for s in sessions:
        if s.chat_id == id:
            return s
    return None

def start(bot, update):
    chatsession = checkforactivesession(update.message.chat_id)
    if chatsession == None or not chatsession.login:
        s = Session(chatid=update.message.chat_id, starttime=datetime.datetime.now())
        ss = Tryloginsession(s, "Login?")
        sessions.append(ss)
        bot.send_message(chat_id=update.message.chat_id, 
            text=ss.reply,
            reply_markup=InlineKeyboardMarkup(ss.keyboard))
    else:
        sessions.remove(chatsession)
        ss = Waitactionsession(chatsession)
        sessions.append(ss)
        if not ss.keyboard is None:
            bot.send_message(chat_id=update.message.chat_id, 
                text=ss.reply,
                reply_markup=InlineKeyboardMarkup(ss.keyboard))
        else:
            bot.send_message(chat_id=update.message.chat_id, text=ss.reply)

    
def handle_text(bot, update):
    chatsession = checkforactivesession(update.message.chat_id)
            
    if chatsession == None or not isinstance(chatsession, TextSession): ##check session created for chat and reply is valid
        bot.send_message(chat_id=update.message.chat_id, text="Type /start to begin")
        return

    res = chatsession.handle(update.message.text, datetime.datetime.now(), update.message.message_id+1)  ##res type = retval
    sessions.remove(chatsession)  ##remove old chatsession from list
    if res is None: ##data unhandled by session
        sessions.append(Waitactionsession(chatsession))
        bot.send_message(chat_id=update.message.chat_id, text='Type /start to begin')
    else:
        if not (res.reply is None):  ##special actions
            if res.reply == "Bye Bye":  ##logout
                bot.send_message(chat_id=update.message.chat_id, text=res.reply)
            else:  ##return to /start menu 
                s = Waitactionsession(res.session, res.reply)
                sessions.append(s)  ##add new session to list, wait for user
                bot.send_message(chat_id=update.message.chat_id, text=s.reply, reply_markup=InlineKeyboardMarkup(s.keyboard))
                if res.reply == "Leave application send to supervisor" and not res.session.admin: ##send message to inform admin leave applied
                    db = DBHelper()
                    super_id = db.findsuper(res.session.dept)
                    db.close()
                    bot.send_message(chat_id=super_id, text=res.session.user + " has applied for leave. Login to check")
                elif res.reply == "Leave rejected": ##send message to inform user leave rejected
                    db = DBHelper()
                    chat_id = db.findchatid(res.session.checkleave)
                    db.close()
                    bot.send_message(chat_id=chat_id, text="Your leave has been rejectd. Login to check")
        else:  ##no special action needed, add new session to list and wait for user action
            sessions.append(res.session)  ##add new session to list, wait for user
            if not res.session.keyboard is None:  #reply_markup = None give error
                bot.send_message(chat_id=update.message.chat_id, text=res.session.reply, reply_markup=InlineKeyboardMarkup(res.session.keyboard))
            else:
                bot.send_message(chat_id=update.message.chat_id, text=res.session.reply)
                
            
def button(bot, update):
    query = update.callback_query
    chatsession = checkforactivesession(query.message.chat_id)
    
    if chatsession == None or not isinstance(chatsession, ButtonSession):  ##check session created for chat and reply is valid
        bot.edit_message_text(chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text='Type /start to begin')
        return
        
    res = chatsession.handle(query.data, datetime.datetime.now(), query.message.message_id)
    sessions.remove(chatsession)
    
    if res is None:
        sessions.append(Waitactionsession(chatsession))
        bot.edit_message_text(chat_id=query.message.chat_id, 
            message_id=query.message.message_id,
            text='Type /start to begin')
    else:  ##special actions
        if not (res.reply is None):  ##data unhandled by session
            if res.reply == "Bye Bye":  ##logout
                bot.edit_message_text(chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=res.reply)
            else:  ##return to /start menu 
                s = Waitactionsession(res.session, res.reply)
                sessions.append(s)  ##add new session to list, wait for user
                bot.edit_message_text(chat_id=query.message.chat_id, 
                    message_id=query.message.message_id,
                    text=s.reply, 
                    reply_markup=InlineKeyboardMarkup(s.keyboard))
                if res.reply == "Leave approved":  ##send message to inform user leave approved
                    db = DBHelper()
                    chat_id = db.findchatid(res.session.checkleave)
                    db.close()
                    bot.send_message(chat_id=chat_id, text="Your leave has been approved. Login to check")
                elif res.reply[-8:] == "canceled" and res.reply[:14] == "Approved Leave":  ##send message to inform admin leave canceled
                    if not res.session.admin:
                        db = DBHelper()
                        super_id = db.findsuper(res.session.dept)
                        db.close()
                        bot.send_message(chat_id=super_id, text=res.reply + " by " + res.session.user)

        else:    ##no special action needed, add new session to list and wait for user action
            sessions.append(res.session)  ##add new session to list, wait for user
            if not res.session.keyboard is None:  #reply_markup = None give error
                bot.edit_message_text(chat_id=query.message.chat_id, 
                    message_id=query.message.message_id,
                    text=res.session.reply, 
                    reply_markup=InlineKeyboardMarkup(res.session.keyboard))
            else:
                bot.edit_message_text(chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=res.session.reply)
            
def timeout(bot, job):
    for s in sessions:
        res = s.timeout(datetime.datetime.now())
        if not res is None:
            sessions.remove(s)
            bot.edit_message_text(chat_id=res[0], 
                message_id=res[1],
                text="You have been logged out", )
            
    
    
def main():
    updater = Updater(token)
    jobqueue = updater.job_queue
    
    #get dispatcher to register handlers
    dispatcher = updater.dispatcher

    #handle commands
    start_handler = CommandHandler('start', start)
    button_handler = CallbackQueryHandler(button)
    reply_handler = MessageHandler(Filters.text, handle_text)

    #add handler to dispatcher
    dispatcher.add_handler(button_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(reply_handler)
    
    jobqueue.run_repeating(timeout, interval=300, first=300)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
