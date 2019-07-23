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
    return 0


@valid_add_keyword_params
@db_session
def add_keyword(feedId, username, keyword):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    Keyword(word=keyword, account=account)
    commit()
    return 0


@valid_delete_account_params
@db_session
def delete_account(feedId, username):
    feedee = Feedee[feedIde]
    Account.get(feedee=Feedee[feedId], username=username).delete()
    commit()
    return 0


@valid_delete_keyword_params
@db_session
def delete_keyword(feedId, username, keyword):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    Keyword.get(word=keyword, account=Account.get(username=username, feedee=keyword.account.feedee)).delete()
    commit()
    return 0


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
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    account.keywordsEnabled = False
    return 0


@valid_account_query_params
@db_session
def enable_keywords(feedId, username):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    account.keywordsEnabled = True
    return 0


###As of now, Pony does not provide bulk inserts
def add_accounts(feedId, usernames):
    errors = []
    for username in usernames:
        try:
            add_account(feedId, username)
        except ValueError as e:
            errors.append((username, e))
    return errors


def add_keywords(feedId, username, keywords):
    errors = []
    for keyword in keywords:
        try:
            add_keyword(feedId, username, keyword)
        except ValueError as e:
            errors.append((username, keyword, e))
    return errors


def delete_accounts(feedId, usernames):
    errors = []
    for username in usernames:
        try:
            delete_account(feedId, username)
        except ValueError as e:
            errors.append((username, e))
    return errors


def delete_keywords(feedId, username, keywords):
    errors = []
    for keyword in keywords:
        try:
            delete_keyword(feedId, username, keyword)
        except ValueError as e:
            errors.append((username, keyword, e))
    return errors