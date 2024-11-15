from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re, threading
all_data = {}

def get_player_data(url):
    driver = webdriver.Chrome()
    driver.get(url)
    player_info = {}
    player_info['team'] = driver.find_element(By.CLASS_NAME, "team").text
    player_info['name'] = driver.find_element(By.CLASS_NAME, "name").text
    while player_info['name'][-1].isdigit():
        player_info['name'] = player_info['name'][:-1]
    player_info['icon'] = get_img_url(driver.find_element(By.CSS_SELECTOR, ".img span"))
    player_info['number'] = driver.find_element(By.CLASS_NAME, "number").text
    player_info['position'] = driver.find_element(By.CSS_SELECTOR, ".pos .desc").text
    player_info['batting_preference'] = driver.find_element(By.CSS_SELECTOR, ".b_t .desc").text
    player_info['birthday'] = driver.find_element(By.CSS_SELECTOR, ".born .desc").text
    player_info['birthplace'] = driver.find_element(By.CSS_SELECTOR, ".nationality .desc").text
    player_info['history_performance'] = []
    table = driver.find_element(By.CSS_SELECTOR, ".RecordTable")
    trs = table.find_elements(By.TAG_NAME, "tr")
    tds = trs[-2].find_elements(By.TAG_NAME, "td")
    for td in tds[1:]:
        player_info['history_performance'].append(td.text)
    all_data['players'].append(player_info)
    driver.quit()

def get_img_url(team):
    base_url = "https://www.cpbl.com.tw"
    team_pic = team.get_attribute("style")
    match = re.search(r'url\("(.*?)"\)', team_pic)
    if match:
        image_url = match.group(1)
        if image_url.startswith("/"):
            image_url = base_url + image_url
        return image_url
    else:
        return None 

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
    info_titles = ['裁判', '比賽時間/觀眾人數']

    try:
        #--------------------------------------- get game info ---------------------------------------
        all_data['場地'] = driver.find_element(By.CLASS_NAME, "place").text
        all_data['場次名稱'] = driver.find_element(By.CLASS_NAME, "game_no").text
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
        all_data['主隊得分'] = team_home.find_element(By.CLASS_NAME, "score").text
        all_data['客隊得分'] = team_away.find_element(By.CLASS_NAME, "score").text
        all_data['主隊總場次(勝負平局)'] = team_home.find_element(By.CLASS_NAME, "w-l-t").text
        all_data['客隊總場次(勝負平局)'] = team_away.find_element(By.CLASS_NAME, "w-l-t").text
        all_data['主隊圖標'] = get_img_url(team_home.find_element(By.CSS_SELECTOR, ".team_name a"))
        all_data['客隊圖標'] = get_img_url(team_away.find_element(By.CSS_SELECTOR, ".team_name a"))
        if all_data['場次名稱'] == '冠軍賽G1':
            all_data['影片連結'] = 'https://www.youtube.com/watch?v=o-6hP9O1dXs&t=274s'
        elif all_data['場次名稱'] == '冠軍賽G2':
            all_data['影片連結'] = 'https://www.youtube.com/watch?v=wK-Xear-tcA&t=306s'
        elif all_data['場次名稱'] == '冠軍賽G3':
            all_data['影片連結'] = 'https://www.youtube.com/watch?v=7ttZgctduiM&t=1343s'
        elif all_data['場次名稱'] == '冠軍賽G4':
            all_data['影片連結'] = 'https://www.youtube.com/watch?v=hXOoe7WfKqI&t=51s'
        elif all_data['場次名稱'] == '冠軍賽G5':
            all_data['影片連結'] = 'https://www.youtube.com/watch?v=YpkL8RlfJ3Y&t=4388s'

        #--------------------------------------- get scoreboard info ---------------------------------------
        linescore_table = driver.find_element(By.CLASS_NAME, "linescore_table")
        all_data['主隊圖標(記分板)'] = get_img_url(linescore_table.find_element(By.CSS_SELECTOR, ".team_name tr.away .short a"))
        all_data['客隊圖標(記分板)'] = get_img_url(linescore_table.find_element(By.CSS_SELECTOR, ".team_name tr.home .short a"))
        all_data['主隊記分板'] = [score.text for score in linescore_table.find_elements(By.CSS_SELECTOR, ".linescore.scrollable .home td")]
        all_data['客隊記分板'] = [score.text for score in linescore_table.find_elements(By.CSS_SELECTOR, ".linescore.scrollable .away td")]
        fixed_home_scores = [score.text for score in linescore_table.find_elements(By.CSS_SELECTOR, ".linescore.fixed .home td")]
        fixed_away_scores = [score.text for score in linescore_table.find_elements(By.CSS_SELECTOR, ".linescore.fixed .away td")]
        all_data['主隊記分板'] += fixed_home_scores
        all_data['客隊記分板'] += fixed_away_scores

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

        #--------------------------------------- get player info ---------------------------------------

        tables = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".RecordTable"))
        )
        away_batter_urls = tables[0].find_elements(By.TAG_NAME, "a")
        away_pitcher_urls = tables[2].find_elements(By.TAG_NAME, "a")
        home_batter_urls = tables[3].find_elements(By.TAG_NAME, "a")
        home_pitcher_urls = tables[5].find_elements(By.TAG_NAME, "a")
        all_data['players'] = []
        threads = []
        for url in away_batter_urls[1:]:
            threads.append(threading.Thread(target=get_player_data, args = (url.get_attribute("href"),)))
        for url in home_batter_urls[1:]:
            threads.append(threading.Thread(target=get_player_data, args = (url.get_attribute("href"),)))
        for url in away_pitcher_urls[1:]:
            threads.append(threading.Thread(target=get_player_data, args = (url.get_attribute("href"),)))
        for url in home_pitcher_urls[1:]:
            threads.append(threading.Thread(target=get_player_data, args = (url.get_attribute("href"),)))
        batch_size = 10  # Adjust based on system capacity

        for i in range(0, len(threads), batch_size):
            batch = threads[i:i + batch_size]
            for thread in batch:
                thread.start()
            for thread in batch:
                thread.join()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
    print(all_data)
    return all_data

get_dashboard_data('https://www.cpbl.com.tw/box/index?gameSno=4&year=2024&kindCode=F')