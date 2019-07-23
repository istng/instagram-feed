from pony.orm import *
from datetime import datetime


db = Database()


class Feedee(db.Entity):
    feedId   = PrimaryKey(int)
    accounts = Set('Account')


class Account(db.Entity):
    username        = Required(str)
    lastRestartDate = Required(datetime)
    keywordsEnabled = Required(bool)
    keywords        = Set('Keyword')
    feedee          = Required(Feedee)
    PrimaryKey(username, feedee)


class Keyword(db.Entity):
    word    = Required(str)
    account = Required('Account')
    PrimaryKey(word, account)