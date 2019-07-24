import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, InlineQueryHandler
from telegram.ext import BaseFilter, MessageHandler, Filters
import logging
import argparse
from datetime import datetime, timedelta
import instagramFeeder


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                       level=logging.INFO)


argumentsDescMsg = 'Bot initialization parameters.'
tokenArgHelp     = 'telegram token'
economyDBHelp    = 'economy DB path'
checkTimeArgHelp = 'time to check for new publications'
userIdArgHelp    = 'telegram user id'


startMsg           = 'Hello! Im the Instagram Feed bot, you can find out what I can do with /help'
helpMsg            = 'This is a list of the functions I know:\n'
noParamsGiven      = 'Please send the command with valid parameters.'


functionsHelp = "/addaccounts username1 username2 username3 ...\nAdds one or more accounts by their usernames.\n\n/addkeywords username keyword1 keyword2 ...\nAdds one or more keywords to the username's account.\n\n/deleteaccounts username1 username2 username3 ...\nDeletes all accounts with given usernames.\n\n/deletekeywords username keyword1 keyword2 ...\nDeletes all given keywords from given username's account.\n\n/enableall username\nEnables all posts from username's account.\n\n/enablekeywords username\nEnables only posts containing the username's account keywords.\n\n/listaccounts\nI'll send a list of all present accounts.\n\n/listkeywords username\nI'll send a list of all the keywords of that username's account."


checkTimeDefault = 24 #in hours


def parse_input():
    parser = argparse.ArgumentParser(description=argumentsDescMsg, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('token', metavar='TOKEN', type=str, help=tokenArgHelp)
    parser.add_argument('economyDB', metavar='ECONOMY DB', type=str, help=economyDBHelp)
    parser.add_argument('-ct', metavar='CHECK TIME', type=int, default=checkTimeDefault, help=checkTimeArgHelp)
    parser.add_argument('-uid', metavar='USER ID', type=int, help=userIdArgHelp)
    args = parser.parse_args()
    return args


#keywords = ' '.join(instagramFeeder.get_keywords(userId, username))
#accountsNames = '\n'.join(instagramFeeder.get_usernames(userId)) what if the userId is new and there are no accounts?
def process_reply_msg(ret):
    return str(ret) #should make the proper reply msgs


def check_user_msg_parameters(func):
    def check_and_call(bot, update):
            chatId = update.message.chat_id
            params = update.message.text.split()[1::]
            if len(params) == 0:
                bot.send_message(chat_id=chatId, text=noParamsGiven)
            else:
                ret = func(bot, update)
                replyMsg = process_reply_msg(ret)
                bot.send_message(chat_id=chatId, text=replyMsg)
    return check_and_call


@check_user_msg_parameters
def add_accounts(bot, update):
    userId = update.message.chat_id
    usernames = update.message.text.split()[1::]
    return instagramFeeder.add_accounts(userId, usernames)


@check_user_msg_parameters
def add_keywords(bot, update):
    userId  = update.message.chat_id
    userMsg = update.message.text.split()[1::]
    username = userMsg[0]
    keywords = userMsg[1::]
    return instagramFeeder.add_keywords(userId, username, keywords)


def list_username_accounts(bot, update):
    chatId = update.message.chat_id
    usernames = instagramFeeder.list_usernames(chatId)
    bot.send_message(chat_id=chatId, text=str(usernames)) #should handle this better


@check_user_msg_parameters
def list_keywords(bot, update):
    userId = update.message.chat_id
    username = update.message.text.split()[1]
    try:
        return instagramFeeder.list_keywords(userId, username)
    except ValueError as e:
        return [(username, e)]


@check_user_msg_parameters
def delete_accounts(bot, update):
    userId = update.message.chat_id
    usernames = update.message.text.split()[1::]
    return instagramFeeder.delete_accounts(userId, usernames)


@check_user_msg_parameters
def delete_keywords(bot, update):
    userId  = update.message.chat_id
    userMsg = update.message.text.split()[1::]
    username = userMsg[0]
    keywords = userMsg[1::]
    return instagramFeeder.delete_keywords(userId, username, keywords)


def enable_all(bot, update):
    userId = update.message.chat_id
    usernames = update.message.text.split()[1::]
    return instagramFeeder.enable_all_many(userId, usernames)
    

def enable_keywords(bot, update):
    userId = update.message.chat_id
    usernames = update.message.text.split()[1::]
    return instagramFeeder.enable_keywords_many(userId, usernames)


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=startMsg)


def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=helpMsg+functionsHelp)


def check_feed(bot, job):
    feedees = instagramFeeder.list_feedees_ids()
    for feedee in feedees:
        #bot.send_message(chat_id=feedee, text='hola mostro, vos sos '+str(feedee))
        usernames = instagramFeeder.list_usernames(feedee)
        for username in usernames:
            posts = instagramFeeder.get_last_posts(feedee, username, 1)
            for post in posts:
                job.context.message.reply_text(post)


#it should enter always, not with the filter text...
def check_feed_job(bot, update, job_queue):
    job = job_queue.run_repeating(check_feed, botArgs.ct, context=update)


def main():
    global botArgs
    botArgs = parse_input()

    instagramFeeder.bind_db('sqlite', botArgs.economyDB)


    updater = Updater(botArgs.token)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, check_feed_job, pass_job_queue=True))
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("help", help))
    updater.dispatcher.add_handler(CommandHandler("addaccounts", add_accounts))
    updater.dispatcher.add_handler(CommandHandler("addkeywords", add_keywords))
    updater.dispatcher.add_handler(CommandHandler("listaccounts", list_username_accounts))
    updater.dispatcher.add_handler(CommandHandler("listkeywords", list_keywords))
    updater.dispatcher.add_handler(CommandHandler("deleteaccounts", delete_accounts))
    updater.dispatcher.add_handler(CommandHandler("deletekeywords", delete_keywords))
    updater.dispatcher.add_handler(CommandHandler("enableall", enable_all))
    updater.dispatcher.add_handler(CommandHandler("enablekeywords", enable_keywords))
    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process_reply_msg receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == "__main__":
    main()
