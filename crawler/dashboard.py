from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, re

def get_team_pic(team):
    base_url = "https://www.cpbl.com.tw"
    team_pic = team.get_attribute("style")
    image_url = re.search(r'url\("(.*?)"\)', team_pic).group(1)
    if image_url.startswith("/"):
        image_url = base_url + image_url
    return image_url

def divide_name(org_data, index):
    for i in range(0, len(org_data)):
        org_data[i] = re.sub(r'[()（）]', "", org_data[i])
    org_data[0] = re.sub(r'^\d+\s', "", org_data[0])

    if len(org_data[0].split()) == 2:
        name, pos = org_data[0].split()
    else:
        name = org_data[0]
        pos = None        
    org_data[0] = name
    if index != 2: org_data.insert(1, pos)
    return org_data
def get_dashboard_data(url):
    driver = webdriver.Chrome()
    driver.get(url)
    all_data = {}
    team_names = ['富邦悍將', '台鋼雄鷹', '中信兄弟', '統一7-ELEVEn獅', '樂天桃猿', '味全龍']  
    table_titles = ['戰況表', '打擊成績', '投手成績']
    info_titles = ['裁判', '比賽時間/觀眾人數']

    try:
        #--------------------------------------- get game info ---------------------------------------
        all_data['場地'] = driver.find_element(By.CLASS_NAME, "place").text
        all_data['場次編號'] = driver.find_element(By.CLASS_NAME, "game_no").text
        all_data['比賽日期'] = driver.find_element(By.CLASS_NAME, "date").text
        item_scoreBoard = driver.find_element(By.CSS_SELECTOR, ".item.ScoreBoard") 
        team_away = item_scoreBoard.find_element(By.CSS_SELECTOR, ".team.away")
        team_home = item_scoreBoard.find_element(By.CSS_SELECTOR, ".team.home")
        home_name = team_home.find_element(By.CLASS_NAME, "team_name").text
        away_name = team_away.find_element(By.CLASS_NAME, "team_name").text
        home_name = home_name.replace("二軍", "")
        away_name = away_name.replace("二軍", "")
        all_data['主隊名稱'] = home_name
        all_data['客隊名稱'] = away_name
        all_data[home_name + '得分'] = team_home.find_element(By.CLASS_NAME, "score").text
        all_data[away_name + '得分'] = team_away.find_element(By.CLASS_NAME, "score").text
        all_data[home_name + '總場次(勝負平局)'] = team_home.find_element(By.CLASS_NAME, "w-l-t").text
        all_data[away_name +'總場次(勝負平局)'] = team_away.find_element(By.CLASS_NAME, "w-l-t").text
        all_data[home_name + '圖標'] = get_team_pic(team_home.find_element(By.CSS_SELECTOR, ".team_name a"))
        all_data[away_name +'圖標'] = get_team_pic(team_away.find_element(By.CSS_SELECTOR, ".team_name a"))
        
        #--------------------------------------- get scoreboard info ---------------------------------------
        linescore_table = driver.find_element(By.CLASS_NAME, "linescore_table")
        all_data[home_name + '圖標(記分板)'] = get_team_pic(linescore_table.find_element(By.CSS_SELECTOR, ".team_name tr.away .short a"))
        all_data[away_name +'圖標(記分板)'] = get_team_pic(linescore_table.find_element(By.CSS_SELECTOR, ".team_name tr.home .short a"))
        all_data[home_name + '記分板'] = [score.text for score in linescore_table.find_elements(By.CSS_SELECTOR, ".linescore.scrollable .home td")]
        all_data[away_name + '記分板'] = [score.text for score in linescore_table.find_elements(By.CSS_SELECTOR, ".linescore.scrollable .away td")]
        fixed_home_scores = [score.text for score in linescore_table.find_elements(By.CSS_SELECTOR, ".linescore.fixed .home td")]
        fixed_away_scores = [score.text for score in linescore_table.find_elements(By.CSS_SELECTOR, ".linescore.fixed .away td")]
        all_data[home_name + '記分板'] += fixed_home_scores
        all_data[away_name + '記分板'] += fixed_away_scores

        #--------------------------------------- get dashboard info ---------------------------------------
        # for team_name in team_names:
        #     try:
        #         time.sleep(1)
        #         team_link = driver.find_element(By.XPATH, f"//a[span[contains(text(), '{team_name}')]]")
        #         team_link.click()
        #         tables = WebDriverWait(driver, 15).until(
        #             EC.presence_of_all_elements_located((By.CLASS_NAME, "RecordTableWrap"))
        #         )
        #         for index in range(0, len(tables)):
        #             rows = tables[index].find_elements(By.TAG_NAME, "tr")
        #             value = []
        #             for row in rows:
        #                 cells = row.find_elements(By.XPATH, ".//td")
        #                 if not cells: continue
        #                 try:
        #                     cells[1] = cells[1].find_element(By.CLASS_NAME, "integer")
        #                 except NoSuchElementException:
        #                     pass
        #                 empty_count = 0
        #                 row_data = []
        #                 for cell in cells:
        #                     row_data.append(cell.text)
        #                     if not cell.text:
        #                         empty_count += 1
        #                 if empty_count != len(cells):
        #                     row_data = divide_name(row_data, index % 3)
        #                     value.append(row_data)
        #             if value:
        #                 all_data[team_name + table_titles[index % 3]] = value
        #     except NoSuchElementException:
        #         pass

        #--------------------------------------- get gaem notes ---------------------------------------
        notes = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "GameNote"))
        )
        for index in range(0, len(notes)):
            rows = notes[index].find_elements(By.TAG_NAME, "li")
            value = []
            for row in rows:
                value.append(row.text)
            all_data[info_titles[index]] = value
        compe_infos = driver.find_elements(By.CSS_SELECTOR, ".district p")
        value = []
        for compe_info in compe_infos:
            value.append(compe_info.text)
        all_data['賽事簡報'] = " ".join(value)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
    return all_data

# get_dashboard_data('https://www.cpbl.com.tw/box/index?year=2024&kindCode=F&gameSno=2')





