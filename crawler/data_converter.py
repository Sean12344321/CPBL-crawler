from typing import List
import json, os
from insert_data import insert_broadcast_data, insert_or_get_player_id, insert_game_data

class batter_performance:
    games_played: int
    plate_appearances: int
    at_bats: int
    runs_batted_in: int
    runs_scored: int
    hits: int
    singles: int
    doubles: int
    triples: int
    home_runs: int
    total_bases: int
    strikeouts: int
    stolen_bases: int 
    on_base_percentage: float
    slugging_percentage: float
    batting_average: float
    double_plays: int
    sacrifice_bunts: int
    sacrifice_flies: int
    walks: int
    intentional_walks: int
    hit_by_pitch: int
    caught_stealing: int
    ground_outs: int
    fly_outs: int
    ground_fly_ratio: float
    stolen_base_percentage: float
    ops: float
    def __init__(self, data):
        self.games_played, self.plate_appearances, self.at_bats, self.runs_batted_in, self.runs_scored, self.hits, self.singles, self.doubles, self.triples, self.home_runs, self.total_bases, self.strikeouts, self.stolen_bases, self.on_base_percentage, self.slugging_percentage, self.batting_average, self.double_plays, self.sacrifice_bunts, self.sacrifice_flies, self.walks, self.intentional_walks, self.hit_by_pitch, self.caught_stealing, self.ground_outs, self.fly_outs, self.ground_fly_ratio, self.stolen_base_percentage, self.ops = data

class pitcher_performance:
    games_played: int
    games_started: int
    relief_appearances: int
    complete_games: int
    shutouts: int
    no_walks_hits: int
    wins: int
    losses: int
    saves: int
    blown_saves: int
    holds: int
    innings_pitched: float
    whip: float
    era: float
    batters_faced: int
    pitches_thrown: int
    hits_allowed: int
    home_runs_allowed: int
    walks: int
    intentional_walks: int
    hit_by_pitch: int
    strikeouts: int
    wild_pitches: int
    balks: int
    runs_allowed: int
    earned_runs: int
    ground_outs: int
    fly_outs: int
    ground_fly_ratio: float
    def __init__(self, data):
        self.games_played, self.games_started, self.relief_appearances, self.complete_games, self.shutouts, self.no_walks_hits, self.wins, self.losses, self.saves, self.blown_saves, self.holds, self.innings_pitched, self.whip, self.era, self.batters_faced, self.pitches_thrown, self.hits_allowed, self.home_runs_allowed, self.walks, self.intentional_walks, self.hit_by_pitch, self.strikeouts, self.wild_pitches, self.balks, self.runs_allowed, self.earned_runs, self.ground_outs, self.fly_outs, self.ground_fly_ratio = data

def save_to_json(data, filename):
    current_folder = os.path.dirname(__file__)
    file_path = os.path.join(current_folder, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def convert_to_numbers(data):
    converted_data = []
    for item in data:
        # Remove any non-numeric characters if necessary, e.g., for '（0）'
        item = item.strip("（)").replace("（", "").replace("）", "")
        
        # Convert to integer if possible, otherwise to float
        if '.' in item:
            converted_data.append(float(item))
        elif item.isdigit():  # Check if it's a whole number
            converted_data.append(int(item))
        else:
            converted_data.append(None)  # Use None for invalid numbers or empty strings
    return converted_data


def convert_dashboard_data_and_insert_to_database(scraped_data):
    player_ids = []
    for player in scraped_data['players']:
        converted_player_data = {
            "team": player.get("team", ""),
            "name": player.get("name", ""),
            "number": player.get("number", ""),
            "position": player.get("position", ""),
            "batting_preference": player.get("batting_preference", ""),
            "birthday": player.get("birthday", ""),
            "birthplace" : player.get("birthplace", ""),
            "icon" : player.get("icon", ""),
            "history_performance": {}
        }
        history_performance = convert_to_numbers(player.get("history_performance", []))
        if player.get("position", "") == "投手":
            if(len(history_performance) != 0):
                converted_player_data["history_performance"] = pitcher_performance(history_performance).__dict__ 
        else:
            if(len(history_performance) > 28): # CPBL filled abunance data 
                history_performance.pop(3)
            if(len(history_performance) != 0):
                converted_player_data["history_performance"] = batter_performance(history_performance).__dict__
        player_ids.append(insert_or_get_player_id(converted_player_data))
    
    converted_game_data = {
        "location": scraped_data.get("場地", ""),
        "game_name": scraped_data.get("場次名稱", ""),
        "date": scraped_data.get("比賽日期", ""),
        "referees": scraped_data.get("裁判", []),
        "home_team_name": scraped_data.get("主隊名稱", ""),
        "away_team_name": scraped_data.get("客隊名稱", ""),
        "home_team_icon": scraped_data.get("主隊圖標", ""),
        "away_team_icon": scraped_data.get("客隊圖標", ""),
        "video_url": scraped_data.get("影片連結", ""),
        "player_ids": player_ids,
    }
    insert_game_data(converted_game_data)
    
def convert_textBroadCast_to_json(scraped_data, Curr_ID, DATE):
    converted_data = {
        "inning_records": scraped_data,
        "game_number": Curr_ID,
        "date": DATE
    }
    save_to_json(converted_data, "text_broadcast_data.json")
    insert_broadcast_data()
# data = {'場地': '台南', '場次名稱': '冠軍賽G4', '比賽日期': '2024/10/05', '主隊名稱': '統一7-ELEVEn獅', '客隊名稱': '味全龍', '主隊得分': '4', '客隊得分': '5', '主隊總場次(勝負平局)': '2W-1L', '客隊總場次(勝負平局)': '1W-2L', '主隊圖標': 'https://www.cpbl.com.tw/files/atts/0L021496167521474259/logo_lions_large.png', '客隊圖標': 'https://www.cpbl.com.tw/files/atts/0L021497849799849722/logo_dragon_large.png', '影片連結': 'https://www.youtube.com/watch?v=hXOoe7WfKqI&t=51s', '主隊圖標(記分板)': 'https://www.cpbl.com.tw/files/atts/0L021497845061333235/logo_dragon.png', '客隊圖標(記分板)': 'https://www.cpbl.com.tw/files/atts/0L021496162893869773/logo_lions.png', '主隊記分板': ['0', '1', '0', '0', '2', '1', '0', '0', '0', '4', '8', '1'], '客隊 記分板': ['1', '0', '0', '2', '0', '2', '0', '0', '0', '5', '9', '2'], '裁判': ['主審鄭惟丞', '一壘審陳乃瑞', '二壘審葉詩維', '三壘審周慶祖', '左線審曾鈞威', '右線審林恩鈺'], '比賽時間/觀眾人數': ['時間03:21', '觀眾0'], '賽事簡報': '技術室人員：林柏安、蘇建文、林國盟、王惠民', 'players': [{'team': '味全龍二軍', 'name': '鄭鎧文', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087782013308634767/28鄭鎧文-1.jpg', 'number': '28', 'position': '左外野手', 'batting_preference': '右投右打', 'birthday': '1991/12/18', 'birthplace': '中華民國', 'history_performance': ['25', '71', '62', '7', '7', '12', '6', '4', '0', '2', '22', '23', '0', '0.296', '0.355', '0.194', '2', '0', '0', '9', '（0）', '0', '0', '11', '16', '0.688', '0.00', '0.651']}, {'team': '味全龍二軍', 'name': '石翔宇', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087781919608130647/72石翔宇2024.jpg', 'number': '72', 'position': '游擊手', 'batting_preference': '右投右打', 'birthday': '1996/11/01', 'birthplace': '中華民國', 'history_performance': ['22', '24', '21', '2', '1', '6', '6', '0', '0', '0', '6', '6', '0', '0.348', '0.286', '0.286', '0', '1', '0', '1', '（0）', '1', '0', '9', '1', '9.000', '0.00', '0.634']}, {'team': '味全龍二軍', 'name': '張祐銘', 'icon': 'https://www.cpbl.com.tw/files/atts/0L088847399842647268/34張祐銘2024.jpg', 'number': '34', 'position': '右外野手', 'batting_preference': '右投左打', 'birthday': '1997/03/15', 'birthplace': '中華民國', 'history_performance': ['71', '222', '190', '16', '23', '49', '43', '3', '3', '0', '58', '30', '7', '0.333', '0.305', '0.258', '5', '6', '3', '16', '（0）', '7', '2', '58', '62', '0.935', '0.78', '0.638']}, {'team': '味全龍', 'name': '陽念祖', 'icon': 'https://www.cpbl.com.tw/files/atts/0N294458050749307006/105陽念祖2024.jpg', 'number': '26', 'position': '游擊手', 'batting_preference': '右投右打', 'birthday': '2005/02/08', 'birthplace': '中華民國', 'history_performance': ['2', '4', '4', '0', '0', '0', '0', '0', '0', '0', '0', '2', '0', '0.000', '0.000', '0.000', '0', '0', '0', '0', '（0）', '0', '0', '2', '0', '0.000', '0.00', '0.000']}, {'team': '味全龍二軍', 'name': '魏全', 'icon': 'https://www.cpbl.com.tw/files/atts/0L088850608736764443/98魏全2024.jpg', 'number': '98', 'position': '捕手', 'batting_preference': '右投右打', 'birthday': '1998/01/13', 'birthplace': '中華民國', 'history_performance': ['1', '3', '3', '1', '0', '1', '1', '0', '0', '0', '1', '2', '0', '0.333', '0.333', '0.333', '0', '0', '0', '0', '（0）', '0', '0', '0', '0', '0.000', '0.00', '0.666']}, {'team': '味全龍', 'name': '陳思仲', 'icon': 'https://www.cpbl.com.tw/files/atts/0L281593137621782872/44陳思仲2024.jpg', 'number': '44', 'position': '二壘手', 'batting_preference': '右投右打', 'birthday': '2000/10/18', 'birthplace': '中華民國', 'history_performance': ['19', '41', '36', '3', '3', '6', '6', '0', '0', '0', '6', '9', '0', '0.211', '0.167', '0.167', '0', '3', '0', '2', '（0）', '0', '0', '14', '10', '1.400', '0.00', '0.378']}, {'team': '味全龍二軍', 'name': '林智勝', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087781867266610909/31林智勝2024.jpg', 'number': '31', 'position': '一壘手', 'batting_preference': '右投右打', 'birthday': '1982/01/01', 'birthplace': '中華民國', 'history_performance': ['28', '73', '68', '7', '6', '15', '9', '4', '1', '1', '24', '15', '0', '0.274', '0.353', '0.221', '2', '0', '0', '5', '（0）', '0', '0', '16', '22', '0.727', '0.00', '0.627']}, {'team': '味全龍二軍', 'name': '全浩瑋', 'icon': 'https://www.cpbl.com.tw/files/atts/0L088844995292889726/22全浩瑋2024.jpg', 'number': '22', 'position': '捕手', 'batting_preference': '右投右打', 'birthday': '1998/05/30', 'birthplace': '中華民國', 'history_performance': ['10', '15', '14', '0', '2', '2', '2', '0', '0', '0', '2', '5', '0', '0.143', '0.143', '0.143', '2', '1', '0', '0', '（0）', '0', '0', '5', '3', '1.667', '0.00', '0.286']}, {'team': '味全龍二軍', 'name': '陳品捷', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087782019383846252/93陳品捷2024.jpg', 'number': '93', 'position': '右外野手', 'batting_preference': '右投左打', 'birthday': '1991/07/23', 'birthplace': '中華民國', 'history_performance': ['50', '150', '125', '11', '8', '26', '22', '4', '0', '0', '30', '25', '0', '0.306', '0.240', '0.208', '2', '6', '1', '18', '（0）', '0', '1', '41', '40', '1.025', '0.00', '0.546']}, {'team': '味全龍二軍', 'name': '吳東融', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087782023007047251/61吳東融2024.jpg', 'number': '61', 'position': '三壘手', 'batting_preference': '右投右打', 'birthday': '1991/09/29', 'birthplace': '中華民國', 'history_performance': ['33', '65', '51', '8', '6', '13', '12', '1', '0', '0', '14', '8', '0', '0.406', '0.275', '0.255', '0', '1', '0', '12', '（0）', '1', '3', '14', '17', '0.824', '0.00', '0.681']}, {'team': '統一7-ELEVEn獅二軍', 'name': '施冠宇', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087782030610975807/3施冠宇2024.jpg', 'number': '3', 'position': '一壘手', 'batting_preference': '右投右打', 'birthday': '1995/12/30', 'birthplace': '中華民國', 'history_performance': ['10', '16', '14', '0', '0', '1', '1', '0', '0', '0', '1', '4', '0', '0.188', '0.071', '0.071', '0', '0', '0', '2', '（0）', '0', '0', '4', '5', '0.800', '0.00', '0.259']}, {'team': '統一7-ELEVEn獅二軍', 'name': '林培緯', 'icon': 'https://www.cpbl.com.tw/files/atts/0N066406714406937119/25林培緯2024.jpg', 'number': '25', 'position': '一壘手', 'batting_preference': '右投右打', 'birthday': '2004/01/26', 'birthplace': '中華民國', 'history_performance': ['14', '40', '38', '5', '4', '10', '7', '2', '0', '1', '15', '6', '0', '0.300', '0.395', '0.263', '3', '0', '0', '1', '（0）', '1', '0', '15', '7', '2.143', '0.00', '0.695']}, {'team': '統一7-ELEVEn獅', 'name': '張皓崴', 'icon': 'https://www.cpbl.com.tw/files/atts/0O058616030406783989/38張皓崴2024.jpg', 'number': '38', 'position': '游擊手', 'batting_preference': '右投左打', 'birthday': '2005/06/03', 'birthplace': '中華民國', 'history_performance': ['6', '7', '7', '0', '0', '1', '1', '0', '0', '0', '1', '2', '0', '0.143', '0.143', '0.143', '0', '0', '0', '0', '（0）', '0', '0', '4', '0', '0.000', '0.00', '0.286']}, {'team': '統一7-ELEVEn獅二軍', 'name': '張偉聖', 'icon': 'https://www.cpbl.com.tw/files/atts/0L088854746420408562/52張偉聖2024.jpg', 'number': '52', 'position': '中外野手', 'batting_preference': '右投左打', 'birthday': '1997/12/07', 'birthplace': '中華民國', 'history_performance': ['13', '11', '11', '0', '2', '1', '1', '0', '0', '0', '1', '3', '0', '0.091', '0.091', '0.091', '0', '0', '0', '0', '（0）', '0', '0', '3', '4', '0.750', '0.00', '0.182']}, {'team': '統一7-ELEVEn獅二軍', 'name': '何恆佑', 'icon': 'https://www.cpbl.com.tw/files/atts/0L088851651816087425/何恆佑2024.jpg', 'number': '7', 'position': '一壘手', 'batting_preference': '右投左打', 'birthday': '2001/10/12', 'birthplace': '中華民國', 'history_performance': ['27', '70', '67', '8', '4', '13', '10', '1', '1', '1', '19', '11', '0', '0.203', '0.284', '0.194', '3', '1', '1', '1', '（0）', '0', '0', '27', '18', '1.500', '0.00', '0.487']}, {'team': '統一7-ELEVEn獅二軍', 'name': '林泓弦', 'icon': 'https://www.cpbl.com.tw/files/atts/0O058616131785517620/67林泓弦2024.jpg', 'number': '67', 'position': '一壘手', 'batting_preference': '右投左打', 'birthday': '2005/08/11', 'birthplace': '中華民國', 'history_performance': ['10', '17', '12', '2', '0', '2', '1', '1', '0', '0', '3', '1', '0', '0.333', '0.250', '0.167', '0', '2', '0', '3', '（0）', '0', '0', '7', '4', '1.750', '0.00', '0.583']}, {'team': '統一7-ELEVEn獅二軍', 'name': '田子杰', 'icon': None, 'number': '49', 'position': '右外野手', 'batting_preference': '左投左打', 'birthday': '2003/09/10', 'birthplace': '中華民國', 'history_performance': ['2', '4', '4', '0', '1', '0', '0', '0', '0', '0', '0', '2', '0', '0.000', '0.000', '0.000', '0', '0', '0', '0', '（0）', '0', '0', '1', '1', '1.000', '0.00', '0.000']}, {'team': '統一7-ELEVEn獅二軍', 'name': '陳維祥', 'icon': 'https://www.cpbl.com.tw/theme/client/images/player_no_img.jpg', 'number': '63', 'position': '左外野手', 'batting_preference': '左投左打', 'birthday': '1999/06/09', 'birthplace': '中華民國', 'history_performance': ['4', '6', '6', '0', '0', '0', '0', '0', '0', '0', '0', '3', '0', '0.000', '0.000', '0.000', '0', '0', '0', '0', '（0）', '0', '0', '0', '3', '0.000', '0.00', '0.000']}, {'team': '統一7-ELEVEn 獅二軍', 'name': '唐肇廷', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087782123257884739/6唐肇廷2024.jpg', 'number': '6', 'position': '中外野手', 'batting_preference': '右投左打', 'birthday': '1987/10/12', 'birthplace': '中華民國', 'history_performance': ['6', '15', '11', '1', '2', '1', '1', '0', '0', '0', '1', '2', '0', '0.333', '0.091', '0.091', '0', '0', '0', '4', '（0）', '0', '0', '5', '3', '1.667', '0.00', '0.424']}, {'team': '統一7-ELEVEn獅二軍', 'name': '羅暐捷', 'icon': 'https://www.cpbl.com.tw/files/atts/0L088856149799849722/8羅暐捷2024.jpg', 'number': '8', 'position': '左外野手', 'batting_preference': '右投左打', 'birthday': '2001/01/15', 'birthplace': '中華民國', 'history_performance': ['1', '4', '4', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0.000', '0.000', '0.000', '0', '0', '0', '0', '（0）', '0', '0', '1', '2', '0.500', '0.00', '0.000']}, {'team': '統一7-ELEVEn獅二軍', 'name': '張翔', 'icon': 'https://www.cpbl.com.tw/files/atts/0L281368646520849370/4張翔2024.jpg', 'number': '4', 'position': '捕手', 'batting_preference': '右投右打', 'birthday': '2003/01/22', 'birthplace': '中華民國', 'history_performance': ['9', '25', '24', '2', '2', '5', '4', '0', '1', '0', '7', '8', '1', '0.240', '0.292', '0.208', '0', '0', '0', '1', '（0）', '0', '0', '4', '7', '0.571', '1.00', '0.532']}, {'team': '味全龍二軍', 'name': '◎王伯洋', 'icon': 'https://www.cpbl.com.tw/files/atts/0N294456895711364852/107王伯洋.jpg', 'number': '107', 'position': '投 手', 'batting_preference': '左投左打', 'birthday': '2000/02/17', 'birthplace': '中華民國', 'history_performance': []}, {'team': '味全龍', 'name': '劉昱言', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087782020192259737/15劉昱言2024.jpg', 'number': '15', 'position': '投手', 'batting_preference': '左投左打', 'birthday': '1994/07/27', 'birthplace': '中華民國', 'history_performance': ['8', '0', '8', '0', '0', '0', '0', '0', '0', '0', '0', '7.0', '1.71', '3.86', '33', '133', '7', '0', '5', '（0）', '1', '6', '0', '0', '3', '3', '6', '8', '0.750']}, {'team': '統一7-ELEVEn獅二軍', 'name': '宋文華', 'icon': 'https://www.cpbl.com.tw/files/atts/0M257683074701603994/97宋文華2024.jpg', 'number': '97', 'position': '投手', 'batting_preference': '右投右打', 'birthday': '1996/09/02', 'birthplace': '中華民國', 'history_performance': ['5', '1', '4', '0', '0', '0', '0', '1', '0', '0', '0', '5.0', '1.80', '3.60', '23', '84', '6', '0', '3', '（0）', '0', '0', '0', '0', '3', '2', '4', '10', '0.400']}, {'team': '統一7-ELEVEn獅', 'name': '柯育民', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087782159265124977/36 柯育民2024.jpg', 'number': '36', 'position': '捕手', 'batting_preference': '右投右打', 'birthday': '1997/11/14', 'birthplace': '中華民國', 'history_performance': ['25', '53', '49', '4', '8', '14', '10', '4', '0', '0', '18', '9', '0', '0.314', '0.367', '0.286', '0', '2', '0', '2', '（0）', '0', '0', '20', '8', '2.500', '0.00', '0.681']}, {'team': '味全龍二軍', 'name': '林鋅杰', 'icon': 'https://www.cpbl.com.tw/files/atts/0N062556009117956717/77林鋅杰.jpg', 'number': '77', 'position': '投手', 'batting_preference': '右投右打', 'birthday': '1999/03/18', 'birthplace': '中華民國', 'history_performance': ['1', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '1.0', '2.00', '9.00', '5', '19', '1', '0', '1', '（0）', '0', '0', '0', '0', '1', '1', '0', '3', '0.000']}, {'team': '味全龍二軍', 'name': '林逸達', 'icon': 'https://www.cpbl.com.tw/files/atts/0L088846831400830673/48林逸達2024.jpg', 'number': '48', 'position': ' 投手', 'batting_preference': '右投右打', 'birthday': '2000/12/26', 'birthplace': '中華民國', 'history_performance': ['13', '0', '13', '0', '0', '0', '1', '1', '0', '0', '2', '13.2', '1.17', '1.98', '57', '196', '8', '1', '8', '（3）', '1', '15', '0', '0', '4', '3', '10', '15', '0.667']}, {'team': '統一7-ELEVEn獅二軍', 'name': '張聖豪', 'icon': 'https://www.cpbl.com.tw/files/atts/0L088840856593363792/46張聖豪2024.jpg', 'number': '46', 'position': '捕手', 'batting_preference': '右投左打', 'birthday': '2001/05/11', 'birthplace': '中華民國', 'history_performance': ['2', '2', '2', '0', '0', '1', '1', '0', '0', '0', '1', '0', '0', '0.500', '0.500', '0.500', '0', '0', '0', '0', '（0）', '0', '0', '1', '0', '0.000', '0.00', '1.000']}, {'team': '味全龍', 'name': '劉家愷', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087781910066736647/87劉家愷2024.jpg', 'number': '87', 'position': '投手', 'batting_preference': '左投左打', 'birthday': '1994/03/25', 'birthplace': '中華民國', 'history_performance': ['1', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '1.0', '2.00', '9.00', '5', '18', '1', '0', '1', ' （0）', '0', '0', '0', '0', '1', '1', '2', '1', '2.000']}, {'team': '味全龍', 'name': '李超', 'icon': 'https://www.cpbl.com.tw/files/atts/0N062555412386889507/0李超2024.jpg', 'number': '0', 'position': '投手', 'batting_preference': '右投右打', 'birthday': '1999/10/23', 'birthplace': '中華民國', 'history_performance': ['12', '0', '12', '0', '0', '0', '0', '0', '0', '0', '2', '15.0', '1.33', '2.40', '63', '238', '18', '1', '2', '（0）', '0', '6', '0', '0', '4', '4', '14', '23', '0.609']}, {'team': '統一7-ELEVEn獅二軍', 'name': '鍾允華', 'icon': 'https://www.cpbl.com.tw/theme/client/images/player_no_img.jpg', 'number': '61', 'position': '投手', 'batting_preference': '右投左打', 'birthday': '2003/09/27', 'birthplace': '中華民國', 'history_performance': []}, {'team': '統一7-ELEVEn獅二軍', 'name': '鄭副豪', 'icon': 'https://www.cpbl.com.tw/files/atts/0N066390532255216501/48鄭副豪2024.jpg', 'number': '48', 'position': '投手', 'batting_preference': '右投右打', 'birthday': '2000/03/03', 'birthplace': '中華民國', 'history_performance': []}, {'team': '統一7-ELEVEn獅二軍', 'name': '鄭鈞仁', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087782034450329754/60鄭鈞仁2024.jpg', 'number': '60', 'position': '投手', 'batting_preference': '右投右打', 'birthday': '1995/11/03', 'birthplace': '中華民國', 'history_performance': ['1', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '1.0', '1.00', '0.00', '4', '17', '1', '0', '0', '（0）', '0', '0', '0', '0', '0', '0', '1', '2', '0.500']}, {'team': '統一7-ELEVEn獅二軍', 'name': '江承峰', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087782152636134454/95江承峰2024.jpg', 'number': '95', 'position': '投手', 'batting_preference': '右投右打', 'birthday': '1988/10/14', 'birthplace': '中華民國', 'history_performance': ['24', '0', '24', '0', '0', '0', '0', '1', '0', '1', '6', '17.2', '2.04', '5.09', '86', '307', '25', '2', '11', '（1）', '1', '12', '1', '0', '13', '10', '20', '17', '1.176']}, {'team': '統一7-ELEVEn獅二軍', 'name': '傅于剛', 'icon': 'https://www.cpbl.com.tw/files/atts/0L087782133131621871/42傅于剛2024.jpg', 'number': '42', 'position': '投手', 'batting_preference': '右投右打', 'birthday': '1988/01/18', 'birthplace': '中華民國', 'history_performance': ['2', '0', '2', '0', '0', '0', '0', '0', '0', '0', '0', '4.0', '1.50', '4.50', '17', '65', '6', '0', '0', '（0）', '0', '1', '0', '0', '2', '2', '5', '5', '1.000']}]}

# convert_dashboard_data_to_json(data)