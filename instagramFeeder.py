from datetime import datetime
import selenium.webdriver as swd
import time
from models import *
from asserts import *
import logging


logFile        = './log_'+datetime.now().strftime('%Y.%m.%d')+'.log'
webBrowser     = swd.Chrome
accountUrl     = 'https://www.instagram.com/%s/'
postUrl        = 'https://www.instagram.com/p/'
scrollDown     = 'window.scrollTo(0, document.body.scrollHeight);'    
datePathOffset = '_1o9PC Nzb55'
xpathCaption   = '//*[@id="react-root"]/section/main/div/div/article/div[2]/div[1]/ul/div[1]/li/div/div/div/span'
xpathError     = '/html/body'
igPageNotFound = 'Sorry, this page isn\'t available.'
numbOfPostsDef = 5
scrapSleepDef  = 10
nToGetDef      = 2


logging.basicConfig(filename=logFile, format='%(asctime)s, %(name)s, %(levelname)s, %(message)s',
    level=logging.INFO)


def bind_db(provider, path):
    db.bind(provider, path, create_db=True)
    db.generate_mapping(create_tables=True)


@valid_add_account_params
@db_session
def add_account(feedId, username):
    feedee = Feedee[feedId]
    Account(username=username, lastUpdatedDate=datetime.now(), keywordsEnabled=False, feedee=feedee)
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


def _get_posts(feedId, username, numberOfPosts, scrapingSleep):
    url = accountUrl%(username)
    browser = webBrowser()
    browser.get(url)
    postsLinks = []
    
    try:
        if igPageNotFound in browser.find_element_by_xpath(xpathError).text:
            time.sleep(scrapingSleep)
            browser.close()
            return postsLinks
    except:
        pass

    while len(postsLinks) < numberOfPosts:
        time.sleep(scrapingSleep)
        links = [a.get_attribute('href') for a in browser.find_elements_by_tag_name('a')]
        for link in links:
            if postUrl in link and link not in postsLinks:
                postsLinks.append(link)
        browser.execute_script(scrollDown)
    browser.close()
    return postsLinks[:numberOfPosts]


@valid_account_query_params
def get_last_posts(feedId, username, numberOfPosts=numbOfPostsDef, scrapingSleep=scrapSleepDef):
    urls = _get_posts(feedId, username, numberOfPosts, scrapingSleep)
    browser = webBrowser()
    postsLinks = []
    dates = []
    for link in urls:
        browser.get(link)
        time.sleep(scrapingSleep)
        date = datetime(year=datetime.now().year-1, month=1, day=1)
        caption = {''}
        try:
            publishTime = browser.page_source
            offset = publishTime.find(datePathOffset)
            date = datetime.strptime(publishTime[offset+24:offset+34], '%Y-%m-%d')
        except:
            logging.error(str(feedId)+', '+username+', '+link+', datetime not found')
        try:
            caption = set(browser.find_element_by_xpath(xpathCaption).text.split())
        except:
            logging.warning(str(feedId)+', '+username+', '+link+', captions not found')
        if _is_newer(feedId, username, date) and (_is_all_enabled(feedId, username) or _contains_any_keyword(feedId, username, caption)):
            postsLinks.append(link)
            dates.append(date)
    browser.close()
    _update_date(feedId, username, dates)
    return postsLinks


@valid_account_query_params
def get_last_n_posts(feedId, username, nToGet=nToGetDef, scrapingSleep=scrapSleepDef):
    urls = _get_posts(feedId, username, nToGet, scrapingSleep)
    postsLinks = []

    if not _is_all_enabled(feedId, username):
        browser = webBrowser()
        for link in urls:
            browser.get(link)
            time.sleep(scrapingSleep)
            caption = {''}
            try:
                caption = set(browser.find_element_by_xpath(xpathCaption).text.split())
                if _contains_any_keyword(feedId, username, caption):
                    postsLinks.append(link)
            except:
                logging.warning(str(feedId)+', '+username+', '+link+', captions not found')
        browser.close()
    else:
        postsLinks = urls
    return postsLinks[:nToGet]