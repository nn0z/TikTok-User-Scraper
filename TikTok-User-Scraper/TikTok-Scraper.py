import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import random
import os
import json
import re


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_config():
    default_config = {
        "min_followers": 0,
        "max_followers": 100000000,
        "max_users": 100
    }
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        return config
    except:
        return default_config


def get_output_file(query):
    safe_query = "".join(c for c in query if c.isalnum() or c in "_-")[:30]
    base_path = os.path.join(OUTPUT_DIR, f"{safe_query}.txt")
    if not os.path.exists(base_path):
        return base_path
    counter = 2
    while True:
        new_path = os.path.join(OUTPUT_DIR, f"{safe_query}({counter}).txt")
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def parse_followers(text):
    if not text or text == "N/A":
        return None
    text = text.strip().upper().replace(",", "")
    try:
        if text.endswith("K"):
            return int(float(text[:-1]) * 1_000)
        if text.endswith("M"):
            return int(float(text[:-1]) * 1_000_000)
        if text.endswith("B"):
            return int(float(text[:-1]) * 1_000_000_000)
        return int(float(text))
    except:
        return None


def extract_card_data(card):
    data = {"name": "N/A", "user": "N/A", "followers": "N/A", "likes": "N/A", "url": "N/A"}
    try:
        paragraphs = card.find_elements(By.XPATH, ".//p")
        texts = [p.text.strip() for p in paragraphs if p.text.strip()]
        if len(texts) >= 1:
            data["name"] = texts[0]
        if len(texts) >= 2:
            data["user"] = texts[1]
        if len(texts) >= 3:
            data["followers"] = texts[2]
        if len(texts) >= 6:
            data["likes"] = texts[5]
        if data["user"] == "N/A" or not data["user"]:
            try:
                img = card.find_element(By.XPATH, ".//img[contains(@alt, 'Avatar for')]")
                alt = img.get_attribute("alt")
                data["user"] = alt.replace("Avatar for ", "").strip()
            except:
                pass
        if data["user"] and data["user"] != "N/A":
            data["url"] = f"https://www.tiktok.com/@{data['user']}"
    except:
        pass
    return data


def scroll_and_check(driver, max_steps=30):
    last_count = len(driver.find_elements(
        By.XPATH, "//div[contains(@class, 'DivSearchUserItemContainer')]"
    ))
    stable_count = 0
    for step in range(max_steps):
        try:
            cards = driver.find_elements(
                By.XPATH, "//div[contains(@class, 'DivSearchUserItemContainer')]"
            )
            if not cards:
                return False
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'end', behavior: 'smooth'});",
                cards[-1]
            )
            time.sleep(random.uniform(0.8, 1.5))
            new_cards = driver.find_elements(
                By.XPATH, "//div[contains(@class, 'DivSearchUserItemContainer')]"
            )
            new_count = len(new_cards)
            if new_count > last_count:
                time.sleep(1.5)
                return True
            is_at_bottom = driver.execute_script(
                "return (window.innerHeight + window.pageYOffset) >= document.body.scrollHeight - 100"
            )
            if is_at_bottom:
                stable_count += 1
                time.sleep(2.5)
                final_cards = driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'DivSearchUserItemContainer')]"
                )
                final_count = len(final_cards)
                if final_count > new_count:
                    return True
                if stable_count >= 2:
                    return False
        except:
            continue
    return False


def search_tiktok_users(query, config):
    output_file = get_output_file(query)
    min_followers = config.get("min_followers", 0)
    max_followers = config.get("max_followers", 100000000)
    max_users = config.get("max_users", 100)

    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--lang=en-US")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = uc.Chrome(options=options)

    try:
        search_url = f"https://www.tiktok.com/search/user?q={query}"
        driver.get(search_url)

        WebDriverWait(driver, 15).until(
            lambda d: len(d.find_elements(By.XPATH, "//div[contains(@class, 'DivSearchUserItemContainer')]")) > 0
        )

        seen_users = set()
        accepted_users = 0

        with open(output_file, "w", encoding="utf-8") as f:
            user_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'DivSearchUserItemContainer')]")
            for card in user_cards:
                if accepted_users >= max_users:
                    break
                data = extract_card_data(card)
                if not data["user"] or data["user"] == "N/A" or data["user"] in seen_users:
                    continue
                followers_num = parse_followers(data["followers"])
                if followers_num is None:
                    continue
                if followers_num < min_followers or followers_num > max_followers:
                    continue
                seen_users.add(data["user"])
                accepted_users += 1
                f.write(f"{data['user']}\n")
                print(f"name: {data['name']}")
                print(f"user: {data['user']}")
                print(f"followers: {data['followers']}")
                print(f"likes: {data['likes']}")
                print(f"url: {data['url']}")
                print("-" * 60)
            f.flush()

            scroll_num = 0
            while accepted_users < max_users:
                scroll_num += 1
                content_loaded = scroll_and_check(driver)
                if not content_loaded:
                    break
                time.sleep(1.0)
                user_cards = driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'DivSearchUserItemContainer')]"
                )
                for card in user_cards:
                    if accepted_users >= max_users:
                        break
                    data = extract_card_data(card)
                    if not data["user"] or data["user"] == "N/A" or data["user"] in seen_users:
                        continue
                    followers_num = parse_followers(data["followers"])
                    if followers_num is None:
                        continue
                    if followers_num < min_followers or followers_num > max_followers:
                        continue
                    seen_users.add(data["user"])
                    accepted_users += 1
                    f.write(f"{data['user']}\n")
                    print(f"name: {data['name']}")
                    print(f"user: {data['user']}")
                    print(f"followers: {data['followers']}")
                    print(f"likes: {data['likes']}")
                    print(f"url: {data['url']}")
                    print("-" * 60)
                f.flush()

    except Exception as e:
        pass
    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    config = load_config()
    search_query = input("Enter a name to search on TikTok: ")
    search_tiktok_users(search_query, config)
    os._exit(0)
