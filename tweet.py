from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
from time import sleep
import traceback
import re
import sqlite3

class Tweet:
    def __init__(self,
            driver: webdriver.Chrome,
            Ad: list
    ):
        self.driver = driver
        self.Ad = Ad

        while True:
            try:
                self.tweet = self.__get_first_tweet()
                
                self.__remove_pinned()

                self.tweet_url, self.retweet = self.__get_tweet_url()
                self.tweet_date = self.__get_tweet_date()
                self.tweet_text = self.__get_tweet_text()
            
            except TypeError:
                self.Ad.append(self.tweet)
                sleep(1)
                driver.execute_script("arguments[0].scrollIntoView();", self.tweet)
                continue

            except Exception:
                print(traceback.format_exc())
                sleep(1)
                # driver.execute_script("arguments[0].scrollIntoView();", self.tweet)
                input("An error occured: ")
                continue
            break

        self.__delete_tweet()

    
    def get_url(self) -> str:
        return self.tweet_url
    
    def get_date(self) -> str:
        return self.tweet_date
    
    def get_text(self) -> str:
        return self.tweet_text
    

    def __get_first_tweet(self) -> WebElement:
        """
        
        """
        while True:
            try:
                tweets = self.driver.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")
                for tweet in tweets:
                    if tweet not in self.Ad:
                        return tweet
            except IndexError:
                sleep(1.5)
                continue
    
    
    def __remove_pinned(self):
        """
        
        """
        while True:
            try:
                if self.tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="socialContext"]').get_attribute("innerText") == "Pinned":
                    print("Skipping pinned...")
                    raise TypeError
                
            except NoSuchElementException:
                pass

            except StaleElementReferenceException:
                sleep(1)
                continue

            break


    def __get_tweet_url(self) -> (str, bool):
        urls = self.tweet.find_elements(By.CSS_SELECTOR, "a")

        if urls[0].get_attribute("href") == urls[1].get_attribute("href"):
            url = urls[3].get_attribute("href")
            re_tweet = False
        else:
            url = urls[4].get_attribute("href")
            re_tweet = True

        return url, re_tweet


    def __get_tweet_date(self) -> str:
        try:
            date_element = self.tweet.find_element(By.CSS_SELECTOR, "time")
            date = date_element.get_attribute("datetime")[:10]
            date = datetime.strptime(date, '%Y-%m-%d')
            return date.strftime('%d/%m/%Y')
        except NoSuchElementException:
            raise TypeError


    def __get_tweet_text(self) -> str:
        try:
            element = self.tweet.find_element(
                By.CSS_SELECTOR, "div[data-testid='tweetText']")

            return element.get_attribute("innerText")
        except NoSuchElementException:
            return ""
    

    def find_all_blockchain_addresses(self, text):
        """
        
        """
        btc_pattern = r'(?:^|\s|\/)(1[a-z0-9A-Z]{25,33})|(?:^|\s|\/)(3[a-z0-9A-Z]{25,33})|(?:^|\s|\/)(bc1[a-z0-9A-Z]{23,42})|(?:^|\s|\/)(bc1p[a-z0-9A-Z]{23,42})'
        eth_pattern = r'(?:^|\s|\/)0x[0-9A-Fa-f]{40}'
        trx_pattern = r'(?:^|\s|\/)T[A-Za-z1-9]{33}'

        addresses = []

        # Bitcoin
        btc_addresses = re.findall(btc_pattern, text)
        for address_tuple in btc_addresses:
            for address in address_tuple:
                if address:
                    address = address.strip()
                    addresses.append((address, 'BTC'))

        # Ethereum
        eth_addresses = re.findall(eth_pattern, text)
        for address in eth_addresses:
            address = address.strip()
            addresses.append((address, 'ETH'))

        # Tron
        trx_addresses = re.findall(trx_pattern, text)
        for address in trx_addresses:
            address = address.strip()
            addresses.append((address, 'TRX'))

        return addresses
    
    def tweet_exists(self, c: sqlite3.Cursor, url: str) -> bool:
        c.execute("SELECT COUNT(*) FROM test_1 WHERE url=?", (url,))
        result = c.fetchone()
        return result[0] > 0

    # def check_media(self):
    #     try:
    #         self.tweet.find_element(By.XPATH, "./div/div/div[2]/div[2]/div[4]")
    #         media = True
    #     except NoSuchElementException:
    #         media = False

    #     return media

    def __delete_tweet(self):
        self.driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, self.tweet)
