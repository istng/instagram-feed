import re
import models as m


validUsername   = '^([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)$'
validKeyword    = '^[^\s]{1,15}$'


@m.db_session
def feedee_not_present_create(*args, **kwargs):
    if not m.Feedee.exists(lambda feedee: feedee.feedId == args[0]):
        m.Feedee(feedId=args[0])


def assert_valid_username(*args, **kwargs):
    if not re.compile(validUsername).match(args[1]):
        raise ValueError('Invalid Instagram username')


def assert_valid_keyword(*args, **kwargs):
    if not re.compile(validKeyword).match(args[2]):
        raise ValueError('Invalid keyword: too long')


@m.db_session
def assert_account_existence(*args, **kwargs):
    feedee = m.Feedee[args[0]]
    if not m.Account.exists(lambda account: account.feedee == feedee and account.username == args[1]):
        raise ValueError('Account does not exists')     


@m.db_session
def assert_account_not_existence(*args, **kwargs):
    feedee = m.Feedee[args[0]]
    if m.Account.exists(lambda account: account.feedee == feedee and account.username == args[1]):
        raise ValueError('Account already exists')        


@m.db_session
def assert_keyword_existence(*args, **kwargs):
    feedee = m.Feedee[args[0]]
    account = m.Account.get(username=args[1], feedee=feedee)
    if not m.Keyword.exists(lambda keyword: keyword.account == account and keyword.word == args[2]):
        raise ValueError('Keyword does not exists')   


@m.db_session
def assert_keyword_not_existence(*args, **kwargs):
    feedee = m.Feedee[args[0]]
    account = m.Account.get(username=args[1], feedee=feedee)
    if m.Keyword.exists(lambda keyword: keyword.account == account and keyword.word == args[2]):
        raise ValueError('Keyword already exists')


def valid_add_account_params(func):
    def check_params(*args, **kwargs):
        feedee_not_present_create(*args, **kwargs)
        assert_valid_username(*args, **kwargs)
        assert_account_not_existence(*args, **kwargs)
        return func(*args, **kwargs)
    return check_params


def valid_add_keyword_params(func):
    def check_params(*args, **kwargs):
        feedee_not_present_create(*args, **kwargs)
        assert_valid_username(*args, **kwargs)
        assert_valid_keyword(*args, **kwargs)
        assert_account_existence(*args, **kwargs)
        assert_keyword_not_existence(*args, **kwargs)
        return func(*args, **kwargs)
    return check_params


def valid_delete_account_params(func):
    def check_params(*args, **kwargs):
        feedee_not_present_create(*args, **kwargs)
        assert_valid_username(*args, **kwargs)
        assert_account_existence(*args, **kwargs)
        return func(*args, **kwargs)
    return check_params


def valid_delete_keyword_params(func):
    def check_params(*args, **kwargs):
        feedee_not_present_create(*args, **kwargs)
        assert_valid_username(*args, **kwargs)
        assert_account_existence(*args, **kwargs)
        assert_keyword_existence(*args, **kwargs)
        return func(*args, **kwargs)
    return check_params


def valid_list_accounts_params(func):
    def check_params(*args, **kwargs):
        feedee_not_present_create(*args, **kwargs)
        return func(*args, **kwargs)
    return check_params


def valid_account_query_params(func):
    def check_params(*args, **kwargs):
        feedee_not_present_create(*args, **kwargs)
        assert_valid_username(*args, **kwargs)
        assert_account_existence(*args, **kwargs)
        return func(*args, **kwargs)
    return check_params