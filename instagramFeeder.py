from datetime import datetime
from selenium.webdriver import Firefox
import time
from models import *
from asserts import *

postUrl    = 'https://www.instagram.com/p/'
scrollDown = 'window.scrollTo(0, document.body.scrollHeight);'    


def bind_db(provider, path):
    db.bind(provider, path, create_db=True)
    db.generate_mapping(create_tables=True)


@valid_add_account_params
@db_session
def add_account(feedId, username):
    feedee = Feedee[feedIde]
    Account(username=username, feedee=feedee)
    commit()
    return #code of success


@valid_add_keyword_params
@db_session
def add_keyword(feedId, username, keyword):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    Keyword(word=keyword, account=account)
    commit()
    return #code of success


@valid_delete_account_params
@db_session
def delete_account(feedId, username):
    feedee = Feedee[feedIde]
    Account.get(feedee=Feedee[feedId], username=username).delete()
    commit()
    return #code of success


@valid_delete_keyword_params
@db_session
def delete_keyword(feedId, username, keyword):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    Keyword.get(word=keyword, account=Account.get(username=username, feedee=keyword.account.feedee)).delete()
    commit()
    return #code of success


@valid_list_accounts_params
def list_accounts(feedId):
    return select(a.username for a in Feedee[feedId].accounts)[:]


@valid_account_query_params
@db_session
def list_keywords(feedId, username):
    feedee = Feedee[feedId]
    account = feedee.accounts.get(username=username, feedee=feedee)
    return select(k.word for k in account.keywords)[:]


@valid_account_query_params
@db_session
def enable_all(feedId, username):
    return


@valid_account_query_params
@db_session
def enable_keywords(feedId, username):
    return


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