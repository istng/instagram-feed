import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, InlineQueryHandler
from telegram.ext import BaseFilter, MessageHandler, Filters
import logging
from datetime import datetime, timedelta
import argparse
import re
import instagramAccountFeed as igaf


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                       level=logging.INFO)


argumentsDescMsg = 'Bot initialization parameters.'
tokenArgHelp     = 'telegram token'
checkTimeArgHelp = 'time to check for new publications'
userIdArgHelp    = 'telegram user id'


startMsg           = 'Hello! Im the Instagram Feed bot, you can find out what I can do with /help'
helpMsg            = 'Here is going to be a brief description of what I can do.' #maybe make functions to ask what each one does separately
addedAccounstMsg   = 'Accounts successfully added!'
addedKeywordsMsg   = 'Keywords successfully added!'
deletedAccountsMsg = 'Accounts successfully deleted.'
deletedKeywordsMsg = 'Keywords successfully deleted.'
enabledAllMsg      = 'All posts enabled!'
enabledKeywordsMsg = 'Only posts containing keywords enabled!'


checkTimeDefault = 24 #in hours


def parse_input():
    parser = argparse.ArgumentParser(description=argumentsDescMsg, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('token', metavar='TOKEN', type=str, help=tokenArgHelp)
    parser.add_argument('-ct', metavar='CHECK TIME', type=int, default=checkTimeDefault, help=checkTimeArgHelp)
    parser.add_argument('-uid', metavar='USER ID', type=int, help=userIdArgHelp)
    args = parser.parse_args()
    return args


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=startMsg)


def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=helpMsg)


def add_accounts(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='hola')
    accounts = update.message.text.split()[1::]
    for account in accounts:
         if account not in accountsFeed: accountsFeed[account] = igaf.account(account, datetime(year=2018, month=3, day=1))
    bot.send_message(chat_id=update.message.chat_id, text=addedAccounstMsg)


def add_keywords(bot, update):
    userMsg = update.message.text.split()[1::]
    account = userMsg[0]
    keywords = set(userMsg[1::])
    accountsFeed[account].add_keywords(keywords)
    bot.send_message(chat_id=update.message.chat_id, text=addedKeywordsMsg)


def list_accounts(bot, update):
    accountsNames = '\n'.join(accountsFeed.keys())
    bot.send_message(chat_id=update.message.chat_id, text=accountsNames)


def list_keywords(bot, update):
    account = update.message.text.split()[1::]
    keywords = accountsFeed[account].get_keywords()
    bot.send_message(chat_id=update.message.chat_id, text=keywords)    


def delete_account(bot, update):
    accounts = update.message.text.split()[1::]
    for account in accounts:
         if account in accountsFeed: del accountsFeed[account]
    bot.send_message(chat_id=update.message.chat_id, text=deletedAccountsMsg)


def delete_keywords(bot, update):
    userMsg = update.message.text.split()[1::]
    account = userMsg[0]
    keywords = set(userMsg[1::])
    accountsFeed[account].delete_keywords(keywords)
    bot.send_message(chat_id=update.message.chat_id, text=deletedKeywordsMsg)


def enable_all(bot, update):
    account = update.message.text.split()[1::]
    if accountsFeed[account].are_keywords_enabled(): accountsFeed[account].toggle_keywords()
    bot.send_message(chat_id=update.message.chat_id, text=enabledAllMsg)


def enable_keywords(bot, update):
    account = update.message.text.split()[1::]
    if not accountsFeed[account].are_keywords_enabled(): accountsFeed[account].toggle_keywords()
    bot.send_message(chat_id=update.message.chat_id, text=enabledKeywordsMsg)


def check_feed(bot, job):
    for account in accountsFeed:
        newPosts = accountsFeed[account].get_last_posts(1)
        for post in newPosts:
            job.context.message.reply_text(post)


#it should enter always, not with the filter text...
def check_feed_job(bot, update, job_queue):
    job = job_queue.run_repeating(check_feed, botArgs.ct, context=update)


def main():
    global botArgs
    botArgs = parse_input()

    global accountsFeed
    accountsFeed = dict()


    updater = Updater(botArgs.token)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, check_feed_job, pass_job_queue=True))
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("help", help))
    updater.dispatcher.add_handler(CommandHandler("addaccount", add_accounts))
    updater.dispatcher.add_handler(CommandHandler("addkeywords", add_keywords))
    updater.dispatcher.add_handler(CommandHandler("listaccounts", list_accounts))
    updater.dispatcher.add_handler(CommandHandler("listkeywords", list_keywords))
    updater.dispatcher.add_handler(CommandHandler("delaccount", delete_account))
    updater.dispatcher.add_handler(CommandHandler("delkeywords", delete_keywords))
    updater.dispatcher.add_handler(CommandHandler("enableall", enable_all))
    updater.dispatcher.add_handler(CommandHandler("enablekeywords", enable_keywords))
    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == "__main__":
    main()
