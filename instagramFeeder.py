from datetime import datetime, timedelta
import requests
import json
from models import *
from asserts import *
import logging


logLevel       = logging.INFO
logFile        = './log_'+datetime.now().strftime('%Y.%m.%d')+'.log'
postLinkStr    = 'https://www.instagram.com/p/'
numbOfPostsDef = 5
nToGetDef      = 2


logging.basicConfig(filename=logFile, format='%(asctime)s, %(name)s, %(levelname)s, %(message)s',
    level=logLevel)
logger = logging.getLogger()


def bind_db(provider, path):
    db.bind(provider, path, create_db=True)
    db.generate_mapping(create_tables=True)


@valid_add_account_params
@db_session
def add_account(feedId, username):
    feedee = Feedee[feedId]
    _get_raw_data_from_json(feedId, username) #checking if account exists
    Account(username=username, lastUpdatedDate=datetime.today()-timedelta(days=1), keywordsEnabled=False, feedee=feedee)
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
    feedee = Feedee[feedId]
    Account.get(username=username, feedee=feedee).delete()
    commit()
    return 0


@valid_delete_keyword_params
@db_session
def delete_keyword(feedId, username, keyword):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    Keyword.get(word=keyword, account=account).delete()
    commit()
    return 0


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


@valid_list_accounts_params
@db_session
def list_usernames(feedId):
    return select(a.username for a in Feedee[feedId].accounts)[:]


@valid_account_query_params
@db_session
def list_keywords(feedId, username):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    return select(k.word for k in account.keywords)[:]


@db_session
def list_feedees_ids():
    return select(f.feedId for f in Feedee)[:]


@db_session
def _is_newer(feedId, username, date):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    return account.lastUpdatedDate < date


@db_session
def _is_all_enabled(feedId, username):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    return not account.keywordsEnabled


@db_session
def _contains_any_keyword(feedId, username, caption):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    keywords = {k.word for k in account.keywords}
    return len(caption.intersection(keywords))!=0


@db_session
def _update_date(feedId, username, dates):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    newestDate = account.lastUpdatedDate
    for date in dates:
        if newestDate < date: newestDate = date
    account.lastUpdatedDate = newestDate


def _get_raw_data_from_json(feedId, username):
    raw = requests.get('https://www.instagram.com/'+username+'/?__a=1')
    raw.raise_for_status()
    return json.loads(raw.text)['graphql']['user']['edge_owner_to_timeline_media']['edges']


def _get_date_from_edge(feedId, edge):
    return datetime.fromtimestamp(edge['node']['taken_at_timestamp'])


def _get_caption_from_edge(feedId, edge):
    if len(edge['node']['edge_media_to_caption']['edges'])!=0:
        return edge['node']['edge_media_to_caption']['edges'][0]['node']['text']
    return ''


def _get_post_shortcode_from_edge(feedId, edge):
    return edge['node']['shortcode']


@valid_account_query_params
def get_last_posts(feedId, username, numberOfPosts=numbOfPostsDef):
    logger.debug(str(feedId)+', '+username+', getting last posts')
    rawData = _get_raw_data_from_json(feedId, username)
    postsLinks = []
    dates = []
    for edge in rawData:
        date = _get_date_from_edge(feedId, edge)
        caption = _get_caption_from_edge(feedId, edge)
        if _is_newer(feedId, username, date) and (_is_all_enabled(feedId, username) or _contains_any_keyword(feedId, username, caption)):
            shortcode = _get_post_shortcode_from_edge(feedId, edge)
            postsLinks.append(postLinkStr+shortcode)
            dates.append(date)
    _update_date(feedId, username, dates)
    return postsLinks[:numbOfPostsDef]


@valid_account_query_params
def get_last_n_posts(feedId, username, nToGet=nToGetDef):
    logger.debug(str(feedId)+', '+username+', getting last n posts')
    rawData = _get_raw_data_from_json(feedId, username)
    postsLinks = []
    for edge in rawData:
        shortcode = _get_post_shortcode_from_edge(feedId, edge)
        postsLinks.append(postLinkStr+shortcode)
    return postsLinks[:nToGet]