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
        item = item.strip("（)").replace("（", "").replace("）", "")
        
        # Convert to integer if possible, otherwise to float
        if '.' in item:
            converted_data.append(float(item))
        elif item.isdigit():  
            converted_data.append(int(item))
        else:
            converted_data.append(None)  
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
    
def convert_textBroadCast_data_and_insert_to_database(scraped_data):
    
    converted_broadcast_data = []
    for data in scraped_data:
        converted_broadcast_data.append({
            "game_id": data.get("game_id", ""),
            "inning_name": data.get("inning_name", ""),
            "inning_time": data.get("inning_time", ""),
            "batter_name": data.get("batter_name", ""),
            "pitcher_name": data.get("pitcher_name", ""),
            "batting_number": data.get("batting_number", ""),
            "batting_order": data.get("batting_order", ""),
            "batting_summary": data.get("batting_summary", ""),
            "batting_result": data.get("batting_result", ""),
            "batting_details": data.get("batting_details", []),
            "current_score": data.get("current_score", ""),
        })
    insert_broadcast_data(converted_broadcast_data)