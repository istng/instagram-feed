from datetime import datetime
from selenium.webdriver import Firefox
import time
from models import *
from asserts import *


accountUrl    = 'https://www.instagram.com/%s/'
postUrl       = 'https://www.instagram.com/p/'
scrollDown    = 'window.scrollTo(0, document.body.scrollHeight);'    
xpathDate     = '//*[@id="react-root"]/section/main/div/div/article/div[2]/div[2]/a/time'
xpathCaption  = '//*[@id="react-root"]/section/main/div/div/article/div[2]/div[1]/ul/div[1]/li/div/div/div/span'
scrapingSleep = 10


def bind_db(provider, path):
    db.bind(provider, path, create_db=True)
    db.generate_mapping(create_tables=True)


@valid_add_account_params
@db_session
def add_account(feedId, username):
    feedee = Feedee[feedId]
    Account(username=username, lastUpdatedDate=datetime.now(), keywordsEnabled=True, feedee=feedee)
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



##Batch functions. As of now Pony does not support them natively.


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


def enable_all_many(feedId, usernames):
    for username in usernames:
        enable_all(feedId, username)


def enable_keywords_many(feedId, usernames):
    for username in usernames:
        enable_keywords(feedId, username)



##Get last posts functions.


@db_session
def list_feedees_ids():
    return select(f.feedId for f in Feedee)[:]


@db_session
def is_newer(feedId, username, date):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    return account.lastUpdatedDate < date


@db_session
def is_all_enabled(feedId, username):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    return not account.keywordsEnabled


@db_session
def contains_any_keyword(feedId, username, caption):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    keywords = {k.word for k in account.keywords}
    return len(caption.intersection(keywords))!=0


@db_session
def update_date(feedId, username, dates):
    feedee = Feedee[feedId]
    account = Account.get(username=username, feedee=feedee)
    newestDate = account.lastUpdatedDate
    for date in dates:
        if newestDate < date: newestDate = date
    account.lastUpdatedDate = newestDate


def get_posts(feedId, username, numberOfPublications):
    url = accountUrl%(username)
    browser = Firefox()
    browser.get(url)
    post_links = []
    while len(post_links) < numberOfPublications:
        links = [a.get_attribute('href') for a in browser.find_elements_by_tag_name('a')]
        for link in links:
            if postUrl in link and link not in post_links:
                post_links.append(link)
        browser.execute_script(scrollDown)
        time.sleep(scrapingSleep)
    else:
        browser.close()
        return post_links[:numberOfPublications]


@valid_account_query_params
def get_last_posts(feedId, username, numberOfPublications=10):
    urls = get_posts(feedId, username, numberOfPublications)
    browser = Firefox()
    postsLinks = []
    dates = []
    for link in urls:
        browser.get(link)
        dateStr = browser.find_element_by_xpath(xpathDate).get_attribute('datetime')[0:9]
        date = datetime.strptime(dateStr, '%Y-%M-%d')
        caption = ''
        try:
            caption = set(browser.find_element_by_xpath(xpathCaption).text.split())
        except:
            print('Primitive log')
        if is_newer(feedId, username, date) and (is_all_enabled(feedId, username) or contains_any_keyword(feedId, username, caption)):
            postsLinks.append(link)
            dates.append(date)
            time.sleep(scrapingSleep)
    browser.close()
    update_date(feedId, username, dates)
    return postsLinks