from datetime import datetime
from selenium.webdriver import Firefox
import time
from models import *
from asserts import *


accountUrl = 'https://www.instagram.com/%s/'
postUrl    = 'https://www.instagram.com/p/'
scrollDown = 'window.scrollTo(0, document.body.scrollHeight);'    


def bind_db(provider, path):
    db.bind(provider, path, create_db=True)
    db.generate_mapping(create_tables=True)


@valid_add_account_params
@db_session
def add_account(feedId, username):
    feedee = Feedee[feedId]
    Account(username=username, lastRestartDate=datetime(year=2018, month=3, day=1), keywordsEnabled=False, feedee=feedee)
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


@db_session
def list_feedees_ids():
    return select(f.feedId for f in Feedee)[:]


@valid_account_query_params
def get_posts(feedId, username, numberOfPublications):
    url = "https://www.instagram.com/" + username + "/"
    browser = Firefox()
    browser.get(url)
    post = 'https://www.instagram.com/p/'
    post_links = []
    while len(post_links) < numberOfPublications:
        links = [a.get_attribute('href') for a in browser.find_elements_by_tag_name('a')]
        for link in links:
            if post in link and link not in post_links:
                post_links.append(link)
        scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
        browser.execute_script(scroll_down)
        time.sleep(10)
    else:
        browser.close()
        return post_links[:numberOfPublications]


def get_last_posts(feedId, username, numberOfPublications=10):
    urls = get_posts(feedId, username, numberOfPublications)
    browser = Firefox()
    post_details = []
    for link in urls:
        browser.get(link)
        age = browser.find_element_by_css_selector('a time').text
        post_details.append(link)
        time.sleep(10)
    browser.close()
    return post_details


"""        if ((not self.are_keywords_enabled()) or self.contains_any_keyword(comment)) and self.is_newer(date):
            dates.append(date)
            post_details.append(link)"""