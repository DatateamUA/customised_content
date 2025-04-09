from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pickle
import os

NAPKIN_URL = "https://napkin.one"
COOKIES_FILE = "napkin_cookies.pkl"

def save_cookies(driver, path):
    with open(path, "wb") as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookies(driver, path):
    with open(path, "rb") as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)

def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def login_and_save_cookies(driver):
    driver.get(NAPKIN_URL)
    print("🔐 Please log in manually to Napkin AI (via Google).")
    time.sleep(60)  # You get 1 minute to log in manually
    save_cookies(driver, COOKIES_FILE)
    print("✅ Cookies saved for future runs!")

def inject_note(driver, note):
    driver.get(NAPKIN_URL)
    time.sleep(5)

    note_box = driver.find_element(By.XPATH, '//textarea[@placeholder="Write something..."]')
    note_box.send_keys(note)
    note_box.send_keys(Keys.RETURN)
    print(f"✅ Note submitted: {note}")
    time.sleep(5)

def scrape_ideas(driver):
    driver.get(NAPKIN_URL)
    time.sleep(5)

    ideas = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="note-content"]')
    print("🧠 Scraped Ideas:")
    for i, idea in enumerate(ideas[:10], start=1):  # Limit to first 10
        print(f"{i}. {idea.text}")

def main():
    driver = start_driver()

    if not os.path.exists(COOKIES_FILE):
        login_and_save_cookies(driver)
        driver.quit()
        return

    driver.get(NAPKIN_URL)
    load_cookies(driver, COOKIES_FILE)
    driver.refresh()
    time.sleep(5)

    # Submit a note
    inject_note(driver, "This is a test note from Selenium 🧪")

    # Scrape top 10 ideas
    scrape_ideas(driver)

    driver.quit()

if __name__ == "__main__":
    main()
