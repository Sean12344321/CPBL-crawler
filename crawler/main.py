from selenium import webdriver
from dashboard import get_dashboard_data
from TextBroadCast import fetch_broadcast_data
from data_converter import update_textBroadCase_data, insert_broadcast_data

#這function是用來選擇日期的，但是我們不需要這個功能
# def select_date(year, month, date, driver):
#     year_list = driver.find_element(By.ID, "SelectYear")
#     month_list = driver.find_element(By.ID, "SelectMonth")
#     try:
#         year_list.find_element(By.XPATH, f"//option[text()='{year}']").click()
#         time.sleep(0.1)
#         month_list.find_element(By.XPATH, f"//option[text()='{month}']").click()
#         time.sleep(0.1)
#         driver.find_element(By.XPATH, f"//select[@id='SelectGameSno']/option[text()='{date}']").click()
#         time.sleep(0.1)
#     except NoSuchElementException:
#         print("No data available for the selected date.")
#         exit()
#     WebDriverWait(driver, 3).until(
#         EC.presence_of_element_located((By.XPATH, "//input[@value='查詢']"))5
#     ).click()


dash_board_url = "https://www.cpbl.com.tw/box/live?gameSno=2&year=2024&kindCode=F"
text_broadcast_url = "https://www.cpbl.com.tw/box/live?gameSno=2&year=2024&kindCode=F"
if __name__ == "__main__":
    # data = get_dashboard_data(dash_board_url)
    # convert_dashboard_data_and_insert_to_database(data)
    data = fetch_broadcast_data(text_broadcast_url)
    insert_broadcast_data(data)