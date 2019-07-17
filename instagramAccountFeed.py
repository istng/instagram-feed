import time
from datetime import datetime
from selenium.webdriver import Firefox


class account:
    def __init__(self, name, date=datetime.now(), keywordsEnabled=True):
        self._name = name
        self._keywords = set()
        self._lastDate = date
        self._keywordsEnabled = keywordsEnabled

        self._accountUrl = 'https://www.instagram.com/'+name+'/'
        self._postUrl    = 'https://www.instagram.com/p/'
        self._scrollDown = 'window.scrollTo(0, document.body.scrollHeight);'


    def get_name(self):
        return self._name


    def toggle_keywords(self):
        self._keywordsEnabled = not self._keywordsEnabled


    def are_keywords_enabled(self):
        return self._keywordsEnabled


    def add_keywords(self, keywords):
        self._keywords.update(keywords)


    def get_keywords(self):
        return self._keywords


    def delete_keywords(self, keywords):
        self._keywords.difference_update(keywords)


    def is_newer(self, date):
        return self._lastDate < date


    def update_with_newer_date(self, dates):
        if len(dates) == 0: return
        newDate = max(dates)
        if self.is_newer(newDate): self._lastDate = newDate


    def contains_any_keyword(self, text):
        return len(self._keywords.intersection(set(text.lower().split()))) != 0


    def get_posts(self, numberOfPublications=10):
        url = self._accountUrl
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


    def get_last_posts(self, numberOfPublications=10):
        urls = self.get_posts(numberOfPublications)
        dates = []
        browser = Firefox()
        post_details = []
        for link in urls:
            browser.get(link)
            age = browser.find_element_by_css_selector('a time').text
            date = datetime.strptime(age, '%B %d, %Y')
            xpath_comment = '//*[@id="react-root"]/section/main/div/div/article/div[2]/div[1]/ul/div[1]/li/div/div/div/span'
            comment = browser.find_element_by_xpath(xpath_comment).text
            if ((not self.are_keywords_enabled()) or self.contains_any_keyword(comment)) and self.is_newer(date):
                dates.append(date)
                post_details.append(link)
            time.sleep(10)
        browser.close()
        self.update_with_newer_date(dates)
        return post_details