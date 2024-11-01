from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, threading, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import get_db_connection
from dashboard import get_dashboard_data
from TextBroadCast import fetch_broadcast_data
from data_converter import convert_dashboard_data_to_json, convert_textBroadCast_to_json
from insert_data import insert_broadcast_data

main_page_url = "https://www.cpbl.com.tw/box"
Curr_ID = 0
DATE = ""
conn = get_db_connection()
#192.168.0.12
#uvicorn main:app --host 192.168.0.12 --port 8000

def select_date(year, month, date, driver):
    year_list = driver.find_element(By.ID, "SelectYear")
    month_list = driver.find_element(By.ID, "SelectMonth")
    try:
        year_list.find_element(By.XPATH, f"//option[text()='{year}']").click()
        time.sleep(0.1)
        month_list.find_element(By.XPATH, f"//option[text()='{month}']").click()
        time.sleep(0.1)
        driver.find_element(By.XPATH, f"//select[@id='SelectGameSno']/option[text()='{date}']").click()
        time.sleep(0.1)
    except NoSuchElementException:
        print("No data available for the selected date.")
        exit()
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, "//input[@value='查詢']"))
    ).click()

def get_dasahboard_data_and_convert(url):
    print("Processing dashboard data...")
    data = get_dashboard_data(url)
    convert_dashboard_data_to_json(data, Curr_ID, DATE)
    print("Dashboard data processed.")

def get_broadcast_data_and_convert(url):
    print("Processing broadcast data...")
    data = fetch_broadcast_data(url)
    convert_textBroadCast_to_json(data, Curr_ID, DATE)
    print("Broadcast data processed.")

def get_game_data(driver):
    time.sleep(3)
    game_canceled = driver.find_elements(By.CLASS_NAME, "game_canceled")
    if game_canceled:
        print("Game canceled")
        return
    dashboard_thread = threading.Thread(target=get_dasahboard_data_and_convert, args=(driver.current_url,))
    broadcast_thread = threading.Thread(target=get_broadcast_data_and_convert, args=(driver.current_url,))
    dashboard_thread.start()
    broadcast_thread.start()
    dashboard_thread.join()
    broadcast_thread.join()
    insert_broadcast_data(conn)
    
if __name__ == "__main__":
    input_date = input("輸入日期(yyyy-mm-dd / latest): ")
    driver = webdriver.Chrome()
    driver.get(main_page_url)
    if input_date != "latest":
        year, month, date = input_date.split('-')
        select_date(int(year), int(month), int(date), driver)
    
    gameList = WebDriverWait(driver, 3).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item.final"))
    )
    DATE = driver.find_element(By.CLASS_NAME, "date").text
    size = len(gameList)
    for index in range(0, size):
        Curr_ID = index + 1
        gameList = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item.final"))
        )
        gameList[index].click()
        get_game_data(driver)
        driver.back()

# if __name__ == "__main__":
#     while True:
#         try:
#             print("開始執行網頁爬取...")
#             web_crawling() 
#             time.sleep(10) 
#         except Exception as e:
#             print(f"執行過程中發生錯誤：{e}")