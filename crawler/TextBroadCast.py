from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re, copy

all_data = []

def get_team_pic(team):
    base_url = "https://www.cpbl.com.tw"
    team_pic = team.get_attribute("style")
    if not team_pic:
        return None
    image_url = re.search(r'url\("(.*?)"\)', team_pic).group(1)
    if image_url.startswith("/"):
        image_url = base_url + image_url
    return image_url


def is_same_thing(a, b):
    keys_to_compare = ['inning', 'batter_name', 'score', 'batting_result', 'pitcher_name', 'pitch_info']
    for key in keys_to_compare:
        if a[key] != b[key]:
            return False
    return True
def fetch_ining_data(inning, driver):
    innings = inning.find_elements(By.CSS_SELECTOR, 'section')
    for inning in innings:
        inning_data = {}
        title = inning.find_element(By.CLASS_NAME, 'title').text    
        title = title.replace('Rakuten Monkeys ', '')
        inning_data['inning'] = title
        inning_data['offense_team_icon'] = get_team_pic(inning.find_element(By.CSS_SELECTOR, ".title a"))
        item_plays = inning.find_elements(By.CSS_SELECTOR, '.item.play')
        for item in item_plays:
            button = WebDriverWait(item, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[title='展開打擊紀錄']"))
            )
            inning_data['pitch_info'] = []
            if button.text != '':
                driver.execute_script("arguments[0].click();", button)
                inning_data['batter_name'] = item.find_element(By.CLASS_NAME, "player").text
                inning_data['batter_img'] = get_team_pic(item.find_element(By.CSS_SELECTOR, ".player a"))
                inning_data['score'] = item.find_element(By.CLASS_NAME, "score").text
                inning_data['batting_result'] = button.text
                pitch_info = WebDriverWait(item, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".detail .call_desc"))
                )
                pitch_name = pitch_info[0].text.split('：')
                inning_data['pitcher_name'] = pitch_name[-1]
                pitch_info = [pitch_info[i].text for i in range(1, len(pitch_info))]
                inning_data['pitch_info'] = pitch_info
                inning_data['scoreChange'] = False
                driver.execute_script("arguments[0].click();", button)
                index = -1
                for data in all_data:
                    if is_same_thing(data, inning_data):
                        index = all_data.index(data)
                        break
                if index == -1:
                    all_data.append(copy.deepcopy(inning_data))
                else:
                    all_data[index]['scoreChange'] = True
            else: pass
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

    inning_sections = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'InningPlays'))
    ) 
    fetch_ining_data(inning_sections[0], driver)
    driver.quit()
    return all_data

# fetch_broadcast_data('https://www.cpbl.com.tw/box/index?year=2024&kindCode=C&gameSno=1')