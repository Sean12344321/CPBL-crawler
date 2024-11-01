import json, os
from typing import List

class Scoreboard:
    innings: List[str]  # 局數
    runs: int           # 得分
    hits: int           # 安打
    errors: int         # 失誤

    def __init__(self, data):
        *self.innings, self.runs, self.hits, self.errors = data
        
class BattleStat:
    name: str            # 名字
    position: str        # 守備位置
    batting_results: List[str]  # 打擊結果
    at_bats: int         # 打數
    hits: int            # 安打
    home_runs: int       # 全壘打
    rbis: int            # 打點
    scores: int          # 得分
    batting_avg: float   # 打擊率

    def __init__(self, data):
        self.name, self.position, *self.batting_results, self.at_bats, self.hits, self.home_runs, self.rbis, self.scores, self.batting_avg = data

class BattingStat:
    name: str                  # 名字
    position: str              # 守備位置
    at_bats: int               # 打數
    scores: int                # 得分
    hits: int                  # 安打
    rbis: int                  # 打點
    doubles: int               # 二安
    triples: int               # 三安
    home_runs: int             # 全壘打
    double_plays: int          # 雙殺打
    walks: int                 # 四壞
    intentional_walks: int     # 故四
    hit_by_pitch: int          # 死球
    strikeouts: int            # 被三振
    sacrifice_hits: int        # 犧打
    sacrifice_flies: int       # 犧飛
    stolen_bases: int          # 盜壘
    caught_stealing: int       # 盜壘刺
    errors: int                # 失誤
    batting_avg: float         # 打擊率

    def __init__(self, data):
        self.name, self.position, self.at_bats, self.scores, self.hits, self.rbis, self.doubles, self.triples, self.home_runs, self.double_plays, self.walks, self.intentional_walks, self.hit_by_pitch, self.strikeouts, self.sacrifice_hits, self.sacrifice_flies, self.stolen_bases, self.caught_stealing, self.errors, self.batting_avg = data

class PitchingStat:
    name: str  # 名字
    innings_pitched: int  # 投球局數
    plate_appearances: int  # 面對打席
    pitches_thrown: int  # 投球數
    strikes: int  # 好球數
    hits: int  # 安打
    home_runs: int  # 全壘打
    walks: int  # 四壞
    intentional_walks: int  # 故四
    hit_by_pitch: int  # 死球
    strikeouts: int  # 奪三振
    wild_pitches: int  # 暴投
    pitcher_fouls: int  # 投手犯規
    earned_runs: int  # 失分
    self_earned_runs: int  # 自責分
    errors: int  # 失誤
    era: float  # 防禦率
    on_base_percentage: float  # 每局被上壘率

    def __init__(self, data):
        self.name, self.innings_pitched, self.plate_appearances, self.pitches_thrown, self.strikes, self.hits, self.home_runs, self.walks, self.intentional_walks, self.hit_by_pitch, self.strikeouts, self.wild_pitches, self.pitcher_fouls, self.earned_runs, self.self_earned_runs, self.errors, self.era, self.on_base_percentage = data

def save_to_json(data, filename):
    current_folder = os.path.dirname(__file__)
    file_path = os.path.join(current_folder, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def convert_dashboard_data_to_json(scraped_data, Curr_ID, DATE):
    converted_data = {
        "game_info": {
            "location": scraped_data.get("場地", ""),
            "game_number": scraped_data.get("場次編號", ""),
            "date": scraped_data.get("比賽日期", ""),
            "umpires": scraped_data.get("裁判", []),
            "game_time_and_attendance": scraped_data.get("比賽時間/觀眾人數", []),
            "brief_report": scraped_data.get("賽事簡報", ""),
        },
        "home_team": {},
        "away_team": {},
    }
    home_team_name = scraped_data.get("主隊名稱", "")
    away_team_name = scraped_data.get("客隊名稱", "")
    if home_team_name:
        converted_data["home_team"] = {
            "name": home_team_name,
            "score": int(scraped_data.get(f"{home_team_name}得分", 0)),
            "total_matches": scraped_data.get(f"{home_team_name}總場次(勝負平局)", ""),
            "icon": scraped_data.get(f"{home_team_name}圖標", ""),
            "scoreboard": {
                "icon": scraped_data.get(f"{home_team_name}圖標(記分板)", ""),
                "scores": Scoreboard(scraped_data.get(f"{home_team_name}記分板", "")).__dict__
            },
            "battle_stats": [BattleStat(data).__dict__ for data in scraped_data.get(f"{home_team_name}戰況表", [])],
            "batting_stats": [BattingStat(data).__dict__ for data in scraped_data.get(f"{home_team_name}打擊成績", [])],
            "pitching_stats": [PitchingStat(data).__dict__ for data in scraped_data.get(f"{home_team_name}投手成績", [])]
        }
    if away_team_name:
        converted_data["away_team"] = {
            "name": away_team_name,
            "score": int(scraped_data.get(f"{away_team_name}得分", 0)),
            "total_matches": scraped_data.get(f"{away_team_name}總場次(勝負平局)", ""),
            "icon": scraped_data.get(f"{away_team_name}圖標", ""),
            "scoreboard": {
                "icon": scraped_data.get(f"{away_team_name}圖標(記分板)", ""),
                "scores": Scoreboard(scraped_data.get(f"{away_team_name}記分板", "")).__dict__
            },
            "battle_stats": [BattleStat(data).__dict__ for data in scraped_data.get(f"{away_team_name}戰況表", [])],
            "batting_stats": [BattingStat(data).__dict__ for data in scraped_data.get(f"{away_team_name}打擊成績", [])],
            "pitching_stats": [PitchingStat(data).__dict__ for data in scraped_data.get(f"{away_team_name}投手成績", [])]
        }
    save_to_json(converted_data, "dashboard_data.json")
    
def convert_textBroadCast_to_json(scraped_data, Curr_ID, DATE):
    converted_data = {
        "inning_records": scraped_data,
        "game_number": Curr_ID,
        "date": DATE
    }
        
    save_to_json(converted_data, "text_broadcast_data.json")

# data = {'場地': '斗六', '場次編號': '冠軍賽G2', '比賽日期': '2024/10/07', '主隊名稱': '味全龍', '客隊名稱': '統一7-ELEVEn獅', '味全龍得分': '6', '統一7-ELEVEn獅得分': '5', '味全龍總場次(勝負平局)': '3W-2L', '統一7-ELEVEn獅總場次(勝負平局)': '2W-3L', '味全龍圖標': 'https://www.cpbl.com.tw/files/atts/0L021497849799849722/logo_dragon_large.png', '統一7-ELEVEn獅圖標': 'https://www.cpbl.com.tw/files/atts/0L021496167521474259/logo_lions_large.png', '味全龍圖標(記分板)': 'https://www.cpbl.com.tw/files/atts/0L021496162893869773/logo_lions.png', '統一7-ELEVEn獅圖標(記分板)': 'https://www.cpbl.com.tw/files/atts/0L021497845061333235/logo_dragon.png', '味全龍記分板': ['0', '1', '0', '0', '3', '0', '0', '0', '1', '0', '1', '6', '11', '2'], '統一7-ELEVEn獅記分板': ['0', '0', '0', '1', '1', '2', '0', '1', '0', '0', '0', '5', '8', '2'], '統一7-ELEVEn獅戰況表': [['田子杰', 'CF', '二滾', '', '', '二滾', '一滾', '', '', '', '', '', '', '3', '0', '0', '0', '0', '0.421'], ['柯育民', 'C', '', '', '', '', '', '', '內安', '二滾', '', '', '右飛', '3', '1', '0', '0', '0', '0.167'], ['林培緯', '3B', '三振', '', '', '二安', '', '中飛', '四壞', '', '中飛', '', '游飛', '5', '1', '0', '0', '1', '0.263'], ['陳維祥', 'DH', '三振', '', '', '一安', '', '左飛', '三振', '', '四壞', '', '四壞', '4', '1', '0', '1', '0', '0.222'], ['唐肇廷', 'LFCF', '', '三飛', '', '二滾', '', '四壞', '雙殺', '', '二滾', '', '右飛', '5', '0', '0', '0', '1', '0.182'], ['楊竣翔', '2B', '', '四壞', '', '投滾', '', '', '', '', '', '', '', '1', '0', '0', '0', '0', '0.250'], ['張聖豪', 'PH', '', '', '', '', '', '死球', '', '', '', '', '', '0', '0', '0', '0', '0', '0.231'], ['林 泓弦', 'PR2B', '', '', '', '', '', '', '', '內安', '一滾', '', '', '2', '1', '0', '0', '2', '0.214'], ['何恆佑', '1B', '', '雙殺', '', '', '四壞', '四壞', '', '犧短誤', '', '四壞', '', '1', '0', '0', '0', '1', '0.200'], ['張皓崴', 'SS', '', '', '一安', '', '一安', '一安', '', '四壞', '', '犧短', '', '3', '3', '0', '2', '0', '0.455'], ['羅暐捷', 'RF', '', '', '一飛', '', '一安', '四壞', '', '左飛', '', '左飛', '', '4', '1', '0', '1', '0', '0.300'], ['張翔', 'C', '', '', '右飛', '', '一飛', '', '', '', '', '', '', '2', '0', '0', '0', '0', '0.100'], ['施冠宇', 'PHLF', '', '', '', '', '', '三滾', '', '', '', '', '', '1', '0', '0', '0', '0', '0.200'], ['張偉聖', 'PHLF', '', '', '', '', '', '', '', '犧飛', '', '三振', '', '1', '0', '0', '1', '0', '0.333'], ['Total', None, '', '', '', '', '', '', '', '', '', '', '', '35', '8', '0', '5', '5', ' ']], '統一7-ELEVEn獅打擊成績': [['田子杰', 'CF', '3', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.421'], ['柯育民', 'C', '3', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.167'], ['林培緯', '3B', '5', '1', '1', '0', '1', '0', '0', '0', '1', '0', '0', '1', '0', '0', '0', '0', '0', '0.263'], ['陳維祥', 'DH', '4', '0', '1', '1', '0', '0', '0', '0', '2', '0', '0', '2', '0', '0', '0', '0', '0', '0.222'], ['唐肇廷', 'LFCF', '5', '1', '0', '0', '0', '0', '0', '1', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0.182'], ['楊竣翔', '2B', '1', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0', '1', '0.250'], ['張聖豪', 'PH', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0.231'], ['林泓弦', 'PR2B', '2', '2', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.214'], ['何恆佑', '1B', '1', '1', '0', '0', '0', '0', '0', '1', '3', '0', '0', '0', '1', '0', '0', '0', '0', '0.200'], ['張皓崴', 'SS', '3', '0', '3', '2', '0', '0', '0', '0', '1', '0', '0', '0', '1', '0', '0', '0', '0', '0.455'], ['羅暐捷', 'RF', '4', '0', '1', '1', '0', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0.300'], ['張翔', 'C', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.100'], ['施冠宇', 'PHLF', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.200'], ['張偉聖', 'PHLF', '1', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0', '1', '0', '1', '0', '0', '0', '0.333'], ['Total', None, '35', '5', '8', '5', '1', '0', '0', '2', '10', '0', '1', '4', '2', '1', '0', '0', '1', ' ']], '統一7-ELEVEn獅投手成績': [['林原裕', '2', '13', '45', '29', '3', '0', '2', '0', '0', '1', '0', '0', '1', '1', '1', '6.00', '3.00'], ['傅于剛', '1', '4', '10', '8', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '6.00', '1.00'], ['劉軒荅', '0', '6', '29', '16', '4', '0', '1', '0', '0', '0', '0', '0', '3', '3', '0', '13.50', '2.50'], ['鍾允華', '0', '2', '6', '4', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.00', '1.20'], ['尹柏淮', '1', '4', '22', '12', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0.00', '1.33'], ['江承峰', '1', '4', '17', '8', '0', '0', '1', '0', '0', '1', '0', '0', '0', '0', '0', '0.00', '0.55'], ['鄭鈞仁', '1', '3', '13', '9', '0', '0', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0.00', '0.00'], ['李其峰', '1', '7', '27', '14', '2', '0', '2', '1', '0', '1', '0', '0', '1', '1', '0', '3.00', '2.00'], ['鄭副豪', '1', '5', '11', '5', '1', '0', '1', '1', '0', '0', '0', '0', '0', '0', '0', '6.75', '2.25'], ['宋文華', '0', '5', '9', '6', '1', '0', '1', '1', '1', '1', '0', '0', '1', '1', '0', '4.91', '1.64'], ['Total', '10', '53', '189', '111', '11', '0', '9', '3', '1', '5', '0', '0', '6', '6', '1', ' ', ' ']], '味全龍戰況表': [['吳東融', '2B', '二失', '', '內安', '', '犧短', '中飛', '', '', ' 二安', '故四', '', '4', '2', '0', '0', '1', '0.227'], ['陽念祖', 'SS', '投滾', '', '犧短', '', '二安', '投滾', '', '', '犧短', '中飛', '', '4', '1', '0', '1', '1', '0.238'], ['陳品捷', 'RF', '中飛', '', '一滾', '', '內安', '', '四壞', '', '二安', '二滾', '', '5', '2', '0', '1', '1', '0.200'], ['林智勝', 'DH', '四壞', '', '四壞', '', '四壞', '', '中飛', '', '故四', '', '', '1', '0', '0', '0', '0', '0.286'], ['林子宸', 'PRDH', '', '', '', '', '', '', '', '', '', '', '死球', '0', '0', '0', '0', '1', '0.400'], ['鄭鎧文', 'LF', '雙殺', '', '三滾', '', '一安', '', '三振', '', '', '', '', '4', '1', '0', '2', '0', '0.222'], ['冉承霖', 'CF', '', '', '', '', '', '', '', '', '', '', '', '0', '0', '0', '0', '0', '0.000'], ['邱辰', 'PHLF', '', '', '', '', '', '', '', '', '內飛', '', '三滾', '2', '0', '0', '0', '0', '0.200'], ['全浩瑋', 'C', '', '三振', '', '右飛', '界飛', '', '三滾', '', '四壞', '', '三振', '5', '0', '0', '0', '0', '0.364'], ['張祐銘', 'CFLFCF', '', '三安', '', '界飛', '左飛', '', '', '一滾', '三振', '', '故四', '5', '1', '0', '0', '1', '0.250'], ['石翔宇', '3B', '', '一 安', '', '游飛', '', '四壞', '', '界飛', '', '一安', '二安', '5', '3', '0', '2', '0', '0.600'], ['陳思仲', '1B', '', '雙殺', '', '', '二安', '中飛', '', '三振', '', '犧短', '', '4', '1', '0', '0', '1', '0.364'], ['Total', None, '', '', '', '', '', '', '', '', '', '', '', '39', '11', '0', '6', '6', ' ']], '味全龍打擊成績': [['吳東融', '2B', '4', '1', '2', '0', '1', '0', '0', '0', '1', '1', '0', '0', '1', '0', '0', '0', '0', '0.227'], ['陽念祖', 'SS', '4', '1', '1', '1', '1', '0', '0', '0', '0', '0', '0', '0', '2', '0', '0', '0', '0', '0.238'], ['陳品捷', 'RF', '5', '1', '2', '1', '1', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0.200'], ['林智勝', 'DH', '1', '0', '0', '0', '0', '0', '0', '0', '4', '1', '0', '0', '0', '0', '0', '0', '0', '0.286'], ['林子宸', 'PRDH', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0.400'], ['鄭鎧文', 'LF', '4', '0', '1', '2', '0', '0', '0', '1', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0.222'], ['冉承霖', 'CF', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.000'], ['邱辰', 'PHLF', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.200'], ['全浩瑋', 'C', '5', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '2', '0', '0', '0', '0', '0', '0.364'], ['張祐銘', 'CFLFCF', '5', '1', '1', '0', '0', '1', '0', '0', '1', '1', '0', '1', '0', '0', '0', '0', '0', '0.250'], ['石翔宇', '3B', '5', '0', '3', '2', '1', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0.600'], ['陳思仲', '1B', '4', '1', '1', '0', '1', '0', '0', '1', '0', '0', '0', '1', '1', '0', '0', '0', '0', '0.364'], ['Total', None, '39', '6', '11', '6', '5', '1', '0', '2', '9', '3', '1', '5', '4', '0', '0', '0', '0', ' ']], '味全龍投手成績': [['黃侰程', '2', '6', '27', '16', '0', '0', '1', '0', '0', '2', '0', '0', '0', '0', '0', '0.00', '0.50'], ['莊玉彬', '1', '3', '15', '9', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.00', '1.00'], ['王伯洋', '0', '4', '13', '8', '2', '0', '0', '0', '0', '0', '1', '0', '1', '1', '0', '3.37', '1.87'], ['李超', '0', '3', '14', '6', '1', '0', '1', '0', '0', '0', '1', '0', '1', '1', '0', '7.71', '2.57'], ['林柏佑', '1', '3', '8', '6', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '3.86', '1.71'], ['張鈞守', '0', '4', '14', '5', '0', '0', '1', '0', '1', '0', '0', '0', '2', '2', '0', '27.00', '1.50'], ['劉家愷', '0', '3', '16', '5', '1', '0', '2', '0', '0', '0', '0', '0', '0', '0', '0', '2.70', '2.40'], ['劉昱言', '1', '7', '27', '16', '2', '0', '1', '0', '0', '1', '0', '0', '1', '0', '2', '0.00', '1.36'], ['林逸達', '1', '4', '21', '11', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0.00', '0.86'], ['森榮鴻', '1', '4', '16', '9', '0', '0', '1', '0', '0', '0', '1', '0', '0', '0', '0', '0.00', '1.00'], ['楊鈺翔', '2', '8', '32', '17', '0', '0', '2', '0', '0', '1', '0', '0', '0', '0', '0', '0.00', '1.00'], ['Total', '11', '49', '203', '108', '8', '0', '10', '0', '1', '4', '3', '0', '5', '4', '2', ' ', ' ']], '裁判': ['主審陳均瑋', '一壘審鄭惟丞', ' 二壘審陳乃瑞', '三壘審范杞平', '左線審葉詩維', '右線審陳勛'], '比賽時間/觀眾人數': ['時間04:56', '觀眾0'], '賽事簡報': '技術室人員：周慶祖、蘇建文、林國盟、王惠民'}

# convert_dashboard_data_to_json(data)