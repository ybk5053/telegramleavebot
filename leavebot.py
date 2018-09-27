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

sessions = []

token = '677641802:AAFFA9eSFHxk_CwdGlbZv1TploStJsNlJ1Q'
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
            
    if chatsession == None:
        bot.send_message(chat_id=update.message.chat_id, text="Type /start to begin")
        return
    
    res = chatsession.handle(update.message.text, datetime.datetime.now(), update.message.message_id+1)
    sessions.remove(chatsession)
    if res is None:
        bot.send_message(chat_id=update.message.chat_id, text='Type /start to begin')
    else:
        if not (res.reply is None):
            if res.reply == "Bye Bye":
                bot.send_message(chat_id=update.message.chat_id, text=res.reply)
            else:
                s = Waitactionsession(res.session, res.reply)
                sessions.append(s)
                bot.send_message(chat_id=update.message.chat_id, text=s.reply, reply_markup=InlineKeyboardMarkup(s.keyboard))
        else:
            sessions.append(res.session)
            if not res.session.keyboard is None:
                bot.send_message(chat_id=update.message.chat_id, text=res.session.reply, reply_markup=InlineKeyboardMarkup(res.session.keyboard))
            else:
                bot.send_message(chat_id=update.message.chat_id, text=res.session.reply)
                
            
def button(bot, update):
    query = update.callback_query
    chatsession = checkforactivesession(query.message.chat_id)
    
    if chatsession == None:
        bot.edit_message_text(chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text='Type /start to begin')
        return
        
    res = chatsession.handle(query.data, datetime.datetime.now(), query.message.message_id)
    sessions.remove(chatsession)
    
    if res is None:
        bot.edit_message_text(chat_id=query.message.chat_id, 
            message_id=query.message.message_id,
            text='Type /start to begin')
    else:
        if not (res.reply is None):
            if res.reply == "Bye Bye":
                bot.edit_message_text(chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=res.reply)
            else:
                s = Waitactionsession(res.session, res.reply)
                sessions.append(s)
                bot.edit_message_text(chat_id=query.message.chat_id, 
                    message_id=query.message.message_id,
                    text=s.reply, 
                    reply_markup=InlineKeyboardMarkup(s.keyboard))
                    
            #if "Leave application send to supervisor" in res.reply:
                #db = DBHelper()
                #bot.send_message(chat_id=db.getsupervisor(res.session.dept), text=res.session.user + ' has applied for leave\n/star to login and view')
                #db.close()
        else:
            sessions.append(res.session)
            if not res.session.keyboard is None:
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
    db = DBHelper()
    db.setup()
    db.close()
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
