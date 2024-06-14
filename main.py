from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from logger import Logger
import json
from tweet import Tweet
import sqlite3
import schedule
import time

start_time = time.time()
scanned_tweets = 0
added_to_db = 0

def main():

    start_time = time.time()

    try:
        driver = open_driver(conf["headless"], conf["userAgent"])

        for url in conf["urls"]:
            driver.get(url)
            set_token(driver, conf["token"])
            driver.get(url)

            log.warning("Starting...")
            data = profile_search(driver, url)

    except Exception as e:
        log.error(f"An error occurred: {e}")

    finally:
        end_time = time.time()  
        elapsed_time = end_time - start_time 

        log.warning(f"Количество просканированных твитов: {scanned_tweets}")
        log.warning(f"Количество твитов, добавленных в БД: {added_to_db}")
        log.warning(f"Время выполнения скрипта: {elapsed_time:.2f} с.")


def profile_search(driver: webdriver.Chrome, url: str):
    global scanned_tweets
    global added_to_db

    limit = 1
    skipped_tweets = 0  # Счетчик пропущенных твитов

    driver.get(url)

    log.warning("Fetching...")
    results = []
    Ad = []

    initialize_database()

    conn = sqlite3.connect("test_1.db")
    c = conn.cursor()

    try:
        while len(results) < limit and skipped_tweets < 1:
            tweet_instance = Tweet(driver, Ad)
            tweet = tweet_instance

            data = {}

            data["URL"] = tweet.get_url()
            data["Date"] = tweet.get_date()
            data["Text"] = tweet.get_text()

            scanned_tweets += 1  # Увеличиваем счётчик просканированных твитов

            if tweet.tweet_exists(c, data["URL"]):
                log.info(f"Skipping existing tweet: {data['URL']}")
                skipped_tweets += 1
                continue

            addresses = tweet.find_all_blockchain_addresses(data['Text'])
            if addresses:
                for address, blockchain in addresses:
                    data['Blockchain Address'] = address
                    data['Blockchain Type'] = blockchain
                    results.append(data)

                    # Сохранение данных в БД
                    c.execute('''INSERT INTO test_1 (url, date, text, blockchain_address, blockchain_type)
                                 VALUES (?, ?, ?, ?, ?)''', (data['URL'], data['Date'], data['Text'], address, blockchain))
                    conn.commit()
                    added_to_db += 1  # Увеличиваем счётчик добавленных в БД твитов

            log.info(f"{len(results)} : {data['URL']}")
    except Exception as e:
        log.error(f"An error occurred during profile search: {e}")
    finally:
        conn.close()

    return results

def open_driver(headless: bool, agent: str) -> webdriver.Chrome:
    options = Options()

    options.add_argument('--log-level=3')
    options.add_argument('ignore-certificate-errors')

    if headless:
        options.add_argument('--headless')

    options.add_argument(f"user-agent={agent}")
    
    driver = webdriver.Chrome(options=options)

    return driver

def set_token(driver: webdriver.Chrome, token: str) -> None:
    src = f"""
            let date = new Date();
            date.setTime(date.getTime() + (7*24*60*60*1000));
            let expires = "; expires=" + date.toUTCString();

            document.cookie = "auth_token={token}"  + expires + "; path=/";
        """
    driver.execute_script(src)

def initialize_database():
    db = sqlite3.connect("test_1.db")
    c = db.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS test_1
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT,
                  date TEXT,
                  text TEXT,
                  blockchain_address TEXT,
                  blockchain_type TEXT)''')

    db.commit()
    db.close()

def load_conf() -> dict:
    with open("./files/conf.json", "r") as file:
        return json.loads(file.read())
    
def run_job():
    log.warning("started...")
    main()
    log.warning("completed.")

if __name__  == "__main__":
    log = Logger()
    try:
        conf = load_conf()
    except Exception:
        log.warning("Sorry, an error occurred. Please check your config file.")
        input("\n\tPress any key to exit...")
    else:
        run_job()
        
        # запускаем задачу каждые X минут
        schedule.every(180).minutes.do(run_job)

        while True:
            schedule.run_pending()
            time.sleep(1)
