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
helpMsg            = 'This is a list of the functions I know:\n'
addedAccounstMsg   = '%s accounts added!'
addedKeywordsMsg   = '%s keywords added!'
deletedAccountsMsg = 'Accounts successfully deleted.'
deletedKeywordsMsg = 'Keywords successfully deleted.'
enabledAllMsg      = 'All posts enabled!'
enabledKeywordsMsg = 'Only posts containing keywords enabled!'
noAccountsGivenMsg = 'No accounts were given.'
invalidAccountMsg  = 'The account "%s" wasnt added because its invalid.'
noKeywordsGivenMsg = 'No keywords were given.'
invalidKeywordMsg  = 'The keyword "%s" wasnt added because its too long.'
accountNotPresent  = 'The account "%s" is not present, please add it before assigning its keywords.'

functionsHelp = "/addaccounts username1 username2 username3 ...\nAdds one or more accounts by their usernames.\n\n/addkeywords username keyword1 keyword2 ...\nAdds one or more keywords to the username's account.\n\n/deleteaccounts username1 username2 username3 ...\nDeletes all accounts with given usernames.\n\n/deletekeywords username keyword1 keyword2 ...\nDeletes all given keywords from given username's account.\n\n/enableall username\nEnables all posts from username's account.\n\n/enablekeywords username\nEnables only posts containing the username's account keywords."


validUsername = '^([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)$'
validKeyword  = '^[^\s]{1,15}$'


checkTimeDefault = 24 #in hours


def parse_input():
    parser = argparse.ArgumentParser(description=argumentsDescMsg, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('token', metavar='TOKEN', type=str, help=tokenArgHelp)
    parser.add_argument('-ct', metavar='CHECK TIME', type=int, default=checkTimeDefault, help=checkTimeArgHelp)
    parser.add_argument('-uid', metavar='USER ID', type=int, help=userIdArgHelp)
    args = parser.parse_args()
    return args


def is_a(validRegex, text):
    return re.compile(validRegex).match(text)


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=startMsg)


def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=helpMsg+functionsHelp)


def add_accounts(bot, update):
    chatId    = update.message.chat_id
    accounts  = update.message.text.split()[1::]
    amntAdded = 'All'
    if len(accounts) == 0:
        bot.send_message(chat_id=chatId, text=noAccountsGivenMsg)
        amntAdded = 'None'
        return
    for account in accounts:
        if not is_a(validUsername, account):
            bot.send_message(chat_id=chatId, text=invalidAccountMsg%(account))
            amntAdded = 'Rest of'
        elif account not in accountsFeed:
            accountsFeed[account] = igaf.account(account, datetime(year=2018, month=3, day=1))
    bot.send_message(chat_id=chatId, text=addedAccounstMsg%(amntAdded))


def add_keywords(bot, update):
    chatId  = update.message.chat_id
    userMsg = update.message.text.split()[1::]
    account = userMsg[0]
    keywords = set(userMsg[1::])
    amntAdded = 'All'
    if len(keywords) == 0:
        bot.send_message(chat_id=chatId, text=noKeywordsGivenMsg)
        amntAdded = 'None'
        return
    for keyword in keywords:
        if not is_a(validKeyword, keyword):
            bot.send_message(chat_id=chatId, text=invalidKeywordMsg%(keyword))
            amntAdded = 'Rest of'
        elif account in accountsFeed:
            accountsFeed[account].add_keyword(keyword)
        else:
            bot.send_message(chat_id=chatId, text=accountNotPresent%(account))
            return
    bot.send_message(chat_id=chatId, text=addedKeywordsMsg%(amntAdded))


def list_accounts(bot, update):
    accountsNames = '\n'.join(accountsFeed.keys())
    bot.send_message(chat_id=update.message.chat_id, text=accountsNames)


def list_keywords(bot, update):
    account = update.message.text.split()[1]
    if account in accountsFeed:
        keywords = ' '.join(accountsFeed[account].get_keywords())
        bot.send_message(chat_id=update.message.chat_id, text=keywords)
    else:
        bot.send_message(chat_id=chatId, text=invalidAccountMsg%(account))



def delete_accounts(bot, update):
    accounts = update.message.text.split()[1::]
    for account in accounts:
        if account in accountsFeed:
            del accountsFeed[account]
        else:
            bot.send_message(chat_id=chatId, text=invalidAccountMsg%(account))    
    bot.send_message(chat_id=update.message.chat_id, text=deletedAccountsMsg)


def delete_keywords(bot, update):
    userMsg = update.message.text.split()[1::]
    account = userMsg[0]
    keywords = set(userMsg[1::])
    if account in accountsFeed:
        accountsFeed[account].delete_keywords(keywords)
        bot.send_message(chat_id=update.message.chat_id, text=deletedKeywordsMsg)
    else:
        bot.send_message(chat_id=chatId, text=invalidAccountMsg%(account))


def enable_all(bot, update):
    chatId = update.message.chat_id
    account = update.message.text.split()[1::]
    if account in accountsFeed:
        if accountsFeed[account].are_keywords_enabled(): accountsFeed[account].toggle_keywords()
        bot.send_message(chat_id=chatId, text=enabledAllMsg)
    else:
        bot.send_message(chat_id=chatId, text=invalidAccountMsg%(account))


def enable_keywords(bot, update):
    chatId = update.message.chat_id
    account = update.message.text.split()[1::]
    if account in accountsFeed:
        if not accountsFeed[account].are_keywords_enabled(): accountsFeed[account].toggle_keywords()
        bot.send_message(chat_id=chatId, text=enabledKeywordsMsg)
    else:
        bot.send_message(chat_id=chatId, text=invalidAccountMsg%(account))


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
    updater.dispatcher.add_handler(CommandHandler("addaccounts", add_accounts))
    updater.dispatcher.add_handler(CommandHandler("addkeywords", add_keywords))
    updater.dispatcher.add_handler(CommandHandler("listaccounts", list_accounts))
    updater.dispatcher.add_handler(CommandHandler("listkeywords", list_keywords))
    updater.dispatcher.add_handler(CommandHandler("delaccounts", delete_accounts))
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
