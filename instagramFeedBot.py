import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, InlineQueryHandler
from telegram.ext import BaseFilter, MessageHandler, Filters
import argparse
import instagramFeeder
import logging


telegramLogger = logging.getLogger('telegram')
telegramLogger.setLevel(logging.INFO)
instagramFeederLogger = logging.getLogger('instagramFeeder')


argumentsDescMsg  = 'Bot initialization parameters.'
tokenArgHelp      = 'telegram token'
feederDBHelp     = 'feeder DB path'
firstCheckArgHelp = 'seconds to make the first check'
checkTimeArgHelp  = 'seconds to check for new publications'
numbOfPostsHelp   = 'posts to check from instagram account'
userIdHelp        = 'user id to limit the bot usage'


startMsg           = 'Hello! Im the Instagram Feed bot, you can find out what I can do with /help'
helpMsg            = 'This is a list of the functions I know:\n'
noParamsGivenMsg   = 'Please send the command with valid parameters.'
noLastPostsMsg     = 'No posts found.'

functionsHelp = "/addaccounts username1 username2 username3 ...\nAdds one or more accounts by their usernames.\n\n/addkeywords username keyword1 keyword2 ...\nAdds one or more keywords to the username's account.\n\n/deleteaccounts username1 username2 username3 ...\nDeletes all accounts with given usernames.\n\n/deletekeywords username keyword1 keyword2 ...\nDeletes all given keywords from given username's account.\n\n/enableall username1 username2 username3 ...\nEnables all posts from each username's account. Set as default.\n\n/enablekeywords username1 username2 username3 ...\nEnables only posts containing each username's account keywords.\n\n/listaccounts\nI'll send a list of all present accounts.\n\n/listkeywords username\nI'll send a list of all the keywords of that username's account.\n\n/getlastposts [amount] username1 username2 ...\nIll search and send you the last [amount] posts of the given username's accounts. If no amount if given, Ill use the default 2. It can take a little time."


checkTimeDefault  = 12*60*60
firstCheckDefault = 60
numberOfPostsDef  = 5
userIdDef         = -1

def parse_input():
    parser = argparse.ArgumentParser(description=argumentsDescMsg, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('token', metavar='TOKEN', type=str, help=tokenArgHelp)
    parser.add_argument('feederDB', metavar='FEEDER DB', type=str, help=feederDBHelp)
    parser.add_argument('-fc', metavar='FIRST CHECK', type=int, default=firstCheckDefault, help=firstCheckArgHelp)
    parser.add_argument('-ct', metavar='CHECK TIME', type=int, default=checkTimeDefault, help=checkTimeArgHelp)
    parser.add_argument('-np', metavar='NUMBER OF POSTS', type=int, default=numberOfPostsDef, help=numbOfPostsHelp)
    parser.add_argument('-uid', metavar='USER ID', type=int, default=userIdDef, help=userIdHelp)
    args = parser.parse_args()
    return args


def log_user_msg(func):
    def log_and_call(bot, update):
        chatId = update.message.chat_id
        params = update.message.text
        instagramFeederLogger.info(str(chatId)+', '+params)
        return func(bot, update)
    return log_and_call


def log_errors(userId, errors):
    if errors!=[]: instagramFeederLogger.error(str(userId)+', '+str(errors))


def check_user_msg_not_empty(func):
    def check_and_call(bot, update):
            chatId = update.message.chat_id
            params = update.message.text.split()[1::]
            if len(params) != 0:
                return func(bot, update)
            bot.send_message(chat_id=chatId, text=noParamsGivenMsg)
    return check_and_call


def tryexcept(errors, func, *args):
    try:
        if len(args)==2:
            return func(args[0], args[1])
        elif len(args)==3:
            return func(args[0], args[1], args[2])
    except ValueError as e:
        errors.append(str(e))
    except instagramFeeder.instaloader.exceptions.InstaloaderException as e:
        errors.append(str(e))


def process_reply_msg(errors):
    replyMsg = 'Command executed excepting: '+str(errors)[1:-1]
    if errors==[]: replyMsg='Command executed successfully!'
    return replyMsg


@log_user_msg
@check_user_msg_not_empty
def add_accounts(bot, update):
    userId = update.message.chat_id
    usernames = update.message.text.split()[1::]
    errors = []
    for username in usernames:
        tryexcept(errors, instagramFeeder.add_account, userId, username)
    log_errors(userId, errors)
    bot.send_message(chat_id=userId, text=process_reply_msg(errors))


@log_user_msg
@check_user_msg_not_empty
def add_keywords(bot, update):
    userId  = update.message.chat_id
    userMsg = update.message.text.split()[1::]
    username = userMsg[0]
    keywords = userMsg[1::]
    errors = []
    for keyword in keywords:
        tryexcept(errors, instagramFeeder.add_keyword, userId, username, keyword)
    log_errors(userId, errors)
    bot.send_message(chat_id=userId, text=process_reply_msg(errors))


@log_user_msg
@check_user_msg_not_empty
def delete_accounts(bot, update):
    userId = update.message.chat_id
    usernames = update.message.text.split()[1::]
    errors = []
    for username in usernames:
        tryexcept(errors, instagramFeeder.delete_account, userId, username)
    log_errors(userId, errors)
    bot.send_message(chat_id=userId, text=process_reply_msg(errors))


@log_user_msg
@check_user_msg_not_empty
def delete_keywords(bot, update):
    userId  = update.message.chat_id
    userMsg = update.message.text.split()[1::]
    username = userMsg[0]
    keywords = userMsg[1::]
    errors = []
    for keyword in keywords:
        tryexcept(errors, instagramFeeder.delete_keyword, userId, username, keyword)
    log_errors(userId, errors)
    bot.send_message(chat_id=userId, text=process_reply_msg(errors))


@log_user_msg
def enable_all(bot, update):
    userId = update.message.chat_id
    usernames = update.message.text.split()[1::]
    errors = []
    for username in usernames:
        tryexcept(errors, instagramFeeder.enable_all, userId, username)
    log_errors(userId, errors)
    bot.send_message(chat_id=userId, text=process_reply_msg(errors))
    

@log_user_msg
def enable_keywords(bot, update):
    userId = update.message.chat_id
    usernames = update.message.text.split()[1::]
    errors = []
    for username in usernames:
        tryexcept(errors, instagramFeeder.enable_keywords, userId, username)
    log_errors(userId, errors)
    bot.send_message(chat_id=userId, text=process_reply_msg(errors))


@log_user_msg
def list_username_accounts(bot, update):
    userId = update.message.chat_id
    usernames = [u for u in instagramFeeder.list_usernames(userId)]
    replyMsg = '\n'.join(usernames)
    if len(usernames)==0:
        replyMsg = 'There are no accounts added yet.'
        instagramFeederLogger.warning(str(userId)+', '+replyMsg)
    bot.send_message(chat_id=userId, text=replyMsg)


@log_user_msg
@check_user_msg_not_empty
def list_keywords(bot, update):
    userId = update.message.chat_id
    username = update.message.text.split()[1]
    replyMsg = ''
    try:
        keywords = [k for k in instagramFeeder.list_keywords(userId, username)]
        if keywords==[]:
            replyMsg = 'There are no keywords added yet for %s.'%(username)
            instagramFeederLogger.warning(str(userId)+', '+replyMsg)
        else: replyMsg = ' '.join(keywords)
    except ValueError as e:
        replyMsg = str(e)
        instagramFeederLogger.error(str(userId)+', '+replyMsg)
    bot.send_message(chat_id=userId, text=replyMsg)


@log_user_msg
@check_user_msg_not_empty
def get_last_n_posts(bot, update):
    userId = update.message.chat_id
    userMsg = update.message.text.split()[1::]
    
    nPosts = 2
    usernames = userMsg[0::]
    try: 
        nPosts = int(userMsg[0])
        usernames = userMsg[1::]
    except: pass

    errors = []
    links = []
    for username in usernames:
        res = tryexcept(errors, instagramFeeder.get_last_n_posts, userId, username, nPosts)
        if res!=None: links+=res
    if len(errors)!=0:
        log_errors(userId, errors)
        bot.send_message(chat_id=userId, text=process_reply_msg(errors))
    if len(links)!=0:
        for link in links:
            instagramFeederLogger.debug(str(userId)+', get_last_n_posts, '+link)
            bot.send_message(chat_id=userId, text=link)
    elif len(errors)==0: bot.send_message(chat_id=userId, text=noLastPostsMsg)



@log_user_msg
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=startMsg)


@log_user_msg
def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=helpMsg+functionsHelp)


def check_feed(bot, job):
    #should improve this
    feedees = instagramFeeder.list_feedees_ids()
    for feedee in feedees:
        usernames = instagramFeeder.list_usernames(feedee)
        for username in usernames:
            posts = instagramFeeder.get_last_posts(feedee, username, botArgs.np)
            for post in posts:
                instagramFeederLogger.debug(str(feedee)+', check_feed, '+post)
                bot.send_message(chat_id=feedee, text=post)


class FilterUserId(BaseFilter):
    def filter(self, message):
        return botArgs.uid==-1 or botArgs.uid == message.from_user.id


def main():
    instagramFeederLogger.info('Started running')
    global botArgs
    botArgs = parse_input()
    instagramFeederLogger.info('Bot arguments: '+str(vars(botArgs)))
    
    instagramFeeder.bind_db('sqlite', botArgs.economyDB)

    filterUseId = FilterUserId()

    updater = Updater(botArgs.token)
    updater.dispatcher.add_handler(CommandHandler('start', start, filterUseId))
    updater.dispatcher.add_handler(CommandHandler('help', help, filterUseId))
    updater.dispatcher.add_handler(CommandHandler('addaccounts', add_accounts, filterUseId))
    updater.dispatcher.add_handler(CommandHandler('addkeywords', add_keywords, filterUseId))
    updater.dispatcher.add_handler(CommandHandler('listaccounts', list_username_accounts, filterUseId))
    updater.dispatcher.add_handler(CommandHandler('listkeywords', list_keywords, filterUseId))
    updater.dispatcher.add_handler(CommandHandler('deleteaccounts', delete_accounts, filterUseId))
    updater.dispatcher.add_handler(CommandHandler('deletekeywords', delete_keywords, filterUseId))
    updater.dispatcher.add_handler(CommandHandler('enableall', enable_all, filterUseId))
    updater.dispatcher.add_handler(CommandHandler('enablekeywords', enable_keywords, filterUseId))
    updater.dispatcher.add_handler(CommandHandler('getlastposts', get_last_n_posts, filterUseId))

    job = updater.job_queue
    job.run_repeating(check_feed, interval=botArgs.ct, first=botArgs.fc)
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process_reply_msg receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == "__main__":
    main()
