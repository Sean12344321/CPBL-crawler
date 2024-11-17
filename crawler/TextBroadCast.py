from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from AI_generation import summarize_game_details
import time, copy

inning_time_table = {
    '1 上': '00:11:45',
    '1 下': '00:18:10',
    '2 上': '00:28:30',
    '2 下': '00:38:30',
    '3 上': '00:46:45',
    '3 下': '01:01:10',
    '4 上': '01:13:25',
    '4 下': '01:18:45',
    '5 上': '01:27:45',
    '5 下': '01:39:10',
    '6 上': '01:57:20',
    '6 下': '02:19:30',
    '7 上': '02:26:15',
    '7 下': '02:35:00',
    '8 上': '02:48:10',
    '8 下': '03:03:05',
    '9 上': '03:18:30',
    '9 下': '03:25:05'
}

all_data = []

def fetch_ining_data(inning, driver):
    innings = inning.find_elements(By.CSS_SELECTOR, 'section')
    for inning in innings:
        inning_data = {}
        inning_name = inning.find_element(By.CLASS_NAME, 'title').text    
        inning_name = inning_name.replace('Rakuten Monkeys ', '')
        inning_data['game_id'] = 1
        inning_data['inning_name'] = inning_name
        time_string = inning_time_table[inning_name]
        inning_data['inning_time'] = datetime.strptime(time_string, "%H:%M:%S").time()
        item_plays = inning.find_elements(By.CSS_SELECTOR, '.item.play')
        index = 0
        for item in item_plays:
            try:
                button = WebDriverWait(item, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[title='展開打擊紀錄']"))
                )
            except Exception:
                button = WebDriverWait(item, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".no-pitch-action-remind"))
                )
            index = index + 1
            inning_data['batting_order'] = index
            inning_data['batting_details'] = []
            driver.execute_script("arguments[0].click();", button)
            inning_data['batter_name'] = item.find_element(By.CLASS_NAME, "player").text
            inning_data['batting_number'] = item.find_element(By.CLASS_NAME, "desc").text.split(' ')[0]
            inning_data['current_score'] = item.find_element(By.CLASS_NAME, "score").text
            inning_data['batting_result'] = button.text
            batting_details = WebDriverWait(item, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".detail .call_desc"))
            )
            pitches_count = WebDriverWait(item, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".detail .pitches_count"))
            )[-1].text
            pitch_name = batting_details[0].text.split('：')
            inning_data['pitcher_name'] = pitch_name[-1]
            batting_details = [batting_details[i].text for i in range(1, len(batting_details))]
            inning_data['batting_details'] = batting_details 
            inning_data['batting_summary'] = summarize_game_details(pitches_count, batting_details)
            driver.execute_script("arguments[0].click();", button)
            all_data.append(copy.deepcopy(inning_data))
            time.sleep(13)
    return all_data

def fetch_broadcast_data(url):
    driver = webdriver.Chrome()
    driver.get(url)
    button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.LINK_TEXT, "文字轉播"))
    )
    button.click()
    tabs = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.InningPlaysGroup .tabs li a'))
    )
    for tab in tabs:
        driver.execute_script("window.scrollTo(0, 0);")
        tab.click()
        inning_sections = driver.find_elements(By.CLASS_NAME, 'InningPlays')
        fetch_ining_data(inning_sections[1], driver)
    driver.quit()
    return all_data