from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
import copy

inning_time_table = {
    '1 上': '00:14:20',
    '1 下': '00:27:40',
    '2 上': '00:36:15',
    '2 下': '00:48:30',
    '3 上': '00:58:00',
    '3 下': '01:01:00',
    '4 上': '01:25:00',
    '4 下': '01:31:10',
    '5 上': '03:17:25',
    '5 下': '03:44:10',
    '6 上': '04:11:20',
    '6 下': '04:27:10',
    '7 上': '04:39:10',
    '7 下': '04:49:30',
    '8 上': '05:12:20',
    '8 下': '05:21:00',
    '9 上': '05:32:10',
    '9 下': '05:54:00',
    '10 上': '06:08:05',
    '10 下': '06:19:00',
    '11 上': '06:28:15',
    '11 下': '06:37:20'
}

all_data = []

def fetch_ining_data(inning, driver):
    innings = inning.find_elements(By.CSS_SELECTOR, 'section')
    for inning in innings:
        inning_data = {}
        inning_name = inning.find_element(By.CLASS_NAME, 'title').text    
        inning_name = inning_name.replace('Rakuten Monkeys ', '')
        inning_data['game_id'] = 3
        inning_data['inning_name'] = inning_name
        time_string = inning_time_table[inning_name]
        inning_data['inning_time'] = datetime.strptime(time_string, "%H:%M:%S").time()
        item_plays = inning.find_elements(By.CSS_SELECTOR, '.item.play')
        batting_order = 0
        for item in item_plays:
            try:
                button = WebDriverWait(item, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[title='展開打擊紀錄']"))
                )
            except Exception:
                button = WebDriverWait(item, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".no-pitch-action-remind"))
                )
            batting_order = batting_order + 1
            inning_data['batting_order'] = batting_order
            inning_data['batting_details'] = []
            inning_data['pitches_count'] = []
            driver.execute_script("arguments[0].click();", button)
            inning_data['batter_name'] = item.find_element(By.CLASS_NAME, "player").text
            inning_data['batting_number'] = item.find_element(By.CLASS_NAME, "desc").text.split(' ')[0]
            inning_data['current_score'] = item.find_element(By.CLASS_NAME, "score").text
            inning_data['batting_result'] = button.text
            batting_details = WebDriverWait(item, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".detail .detail_item"))
            )
            pitch_name = batting_details[0].text.split('：')
            inning_data['pitcher_name'] = pitch_name[-1]
            for index, item in enumerate(batting_details):
                if index == 0:
                    continue
                
                call_desc = item.find_element(By.CLASS_NAME, "call_desc").text
                try:
                    pitch_count = item.find_element(By.CLASS_NAME, "pitches_count").text
                except:
                    pitch_count = "NULL"
                inning_data["batting_details"].append(call_desc)
                inning_data['pitches_count'].append(pitch_count)
            
            driver.execute_script("arguments[0].click();", button)
            all_data.append(copy.deepcopy(inning_data))
            print(inning_data)
    return all_data

def fetch_broadcast_data(url):
    driver = webdriver.Chrome()
    driver.get(url)
    tabs = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.InningPlaysGroup .tabs li a'))
    )
    for tab in tabs:
        driver.execute_script("window.scrollTo(0, 0);")
        tab.click()
        inning_sections = driver.find_elements(By.CLASS_NAME, 'InningPlays')
        fetch_ining_data(inning_sections[1], driver)
    driver.quit()
    print(all_data)
    return all_data