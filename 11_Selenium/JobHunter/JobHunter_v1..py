from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("https://www.pracuj.pl")

input("Kliknij AKCEPTUJ i naciśnij Enter...")

time.sleep(2)

search_box = driver.find_element(By.NAME, "kw")
search_box.click()

time.sleep(1)

active_input = driver.switch_to.active_element
active_input.send_keys("Junior QA")

time.sleep(1)

search_button = driver.find_element(
    By.XPATH,
    "//button[contains(., 'Szukaj')]"
)

driver.execute_script("arguments[0].click();", search_button)

time.sleep(5)

input("Naciśnij Enter, aby zakończyć...")