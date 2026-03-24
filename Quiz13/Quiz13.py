# Quiz 13: Get Clicky With It
# Bibek Thapa

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    driver.get("https://books.toscrape.com/")
    time.sleep(2)

    title_elements = driver.find_elements(By.CSS_SELECTOR, "article.product_pod h3 a")
    titles = [item.get_attribute("title") for item in title_elements]

    print("Book titles found:")
    for i, title in enumerate(titles, start=1):
        print(f"{i}. {title}")

    if title_elements:
        print("\nClicking the first book...")
        title_elements[0].click()
        time.sleep(5)

finally:
    driver.quit()