import re
from datetime import datetime
from selenium.webdriver import Firefox
import time
from models import *


validUsername   = '^([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)$'
validKeyword    = '^[^\s]{1,15}$'


postUrl    = 'https://www.instagram.com/p/'
scrollDown = 'window.scrollTo(0, document.body.scrollHeight);'    


def bind_db(provider, path):
    db.bind(provider, path, create_db=True)
    db.generate_mapping(create_tables=True)


def check_feed_id(func):
    @db_session
    def if_not_present_create(*args, **kwargs):
        if not Feedee.exists(lambda feedee: feedee.feedId == args[0]):
            Feedee(feedId=args[0])
        return func(*args, **kwargs)
    return if_not_present_create


def check_username(func):
    def if_valid_continue(*args, **kwargs):
        if not re.compile(validUsername).match(args[1]):
            return #code of invalid username
        return func(*args, **kwargs)
    return if_valid_continue


def check_keyword(func):
    def if_valid_continue(*args, **kwargs):
        if not re.compile(validKeyword).match(args[1]):
            return #code of invalid username
        return func(*args, **kwargs)
    return if_valid_continue


@check_username
@check_feed_id
@db_session
def add_account(feedId, username):
	feedee = Feedee[feedIde]
    if not Account.exists(lambda account: account.username == username and account.feedee != feedee):
        Account(username=username, feedee=feedee)
        commit()
        return #code of success
    else:
        return #code of already exists


@check_username
@check_keyword
@check_feed_id
@db_session
def add_keyword(feedId, username, keyword):
    if not Account.exists(lambda account: account.username == username and account.feedee.feedId != feedId):
        return #code of username not present
    if not Keyword.exists(lambda keyword: keyword.word == keyword and keyword.account.username == username and keyword.account.feedee.feedId == feedId):
        Keyword(word=keyword, account=Account[username])
        commit()
    else:
        return #code of already exists


@check_username
@check_feed_id
@db_session
def delete_account(feedId, username):
    if Account.exists(lambda account: account.username == username and account.feedee.feedId == feedId):
        Account.get(feedee=Feedee[feedId], username=username).delete()
        commit()
        return #code of success
    else:
        return #code of does not exists


@check_username
@check_keyword
@check_feed_id
@db_session
def delete_keyword(feedId, username, keyword):
    if Keyword.exists(lambda keyword: keyword.word == keyword and keyword.account.username == username and keyword.account.feedee.feedId == feedId):
        Keyword.get(word=keyword, account=Account.get(username=username, feedee=keyword.account.feedee)).delete()
        commit()
        return #code of success
    else:
        return #code of does not exists


@check_feed_id
@db_session
def list_accounts(feedId):
    accounts = select(a.username for a in Feedee[feedId].accounts)[:]
    if len(accounts)==0: return #code of no accounts added yet
    return accounts


@check_username
@check_feed_id
@db_session
def list_keywords(feedId, username):
	account = Feedee[feedId].accounts.get(username=username, feedee=Feedee[feedId])
    keywords = select(k.word for k in account.keywords)[:]
    if len(keywords)==0: return #code of no keywords added yet
    return keywords    


###As of now, Pony does not provide bulk inserts
def add_accounts(feedId, usernames):
    #incremental code
    for username in usernames:
        add_account(feedId, username)
    #return incremental code


def add_keywords(feedId, username, keywords):
    #incremental code
    for keyword in keywords:
        add_account(feedId, username, keyword)
    #return incremental code    


def delete_accounts(feedId, usernames):
    #incremental code
    for username in usernames:
        delete_account(feedId, username)
    #return incremental code


def delete_keywords(feedId, username, keywords):
    #incremental code
    for keyword in keywords:
        delete_account(feedId, username, keyword)
    #return incremental code    