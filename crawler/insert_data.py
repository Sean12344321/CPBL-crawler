import json, os, sys
from psycopg2.extras import DictCursor
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import get_db_connection

conn = get_db_connection()

def insert_broadcast_data():
    json_file = os.path.join(os.path.dirname(__file__), "text_broadcast_data.json")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cur = conn.cursor()
    insert_query = """
        INSERT INTO batting_info (
            game_number, game_date, inning, team_logo, batter_name, batter_avatar,
            pitcher_name, pitching_info, score, batting_result, score_change
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    check_query = """
        SELECT 1 FROM batting_info WHERE game_number = %s AND game_date = %s
    """

    cur.execute(check_query, (data["game_number"], data["date"]))
    result = cur.fetchone()
    if result:
        print(f"batting_info for game {data['game_number']} on {data['date']} already exists.")
    else :
        for record in data["inning_records"]:
            cur.execute(insert_query, (
                data["game_number"],
                data["date"],
                record["inning"],
                record["offense_team_icon"],
                record["batter_name"],
                record["batter_img"],
                record["pitcher_name"],
                record["pitch_info"],   
                record["score"],
                record["batting_result"],
                record["scoreChange"]
            ))
        print(f"batting_info for game {data['game_number']} on {data['date']} inserted to database.")
    conn.commit()
    cur.close()

def insert_or_get_player_id(data):

    cur = conn.cursor(cursor_factory=DictCursor)

    insert_query = """
    INSERT INTO player_info (team, name, number, position, batting_preference, birthday, birthplace, icon, history_performance)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    check_query = """
    SELECT id FROM player_info WHERE team = %s AND number = %s
    """

    cur.execute(check_query, (data["team"], data["number"]))
    result = cur.fetchone()
    if(result):
        return result["id"]
    else:
        cur.execute(
        insert_query,
            (
                data['team'],
                data['name'],
                data['number'],
                data['position'],
                data['batting_preference'],
                datetime.strptime(data['birthday'], '%Y/%m/%d'),  # Convert to date
                data['birthplace'],
                data['icon'],
                json.dumps(data['history_performance'])  # Convert to JSON
            )
        )

    new_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    return new_id

def insert_game_data(data):
    cur = conn.cursor()
    insert_query = """
    INSERT INTO game (game_name, date, video_url, home_team_name, away_team_name, home_team_icon, away_team_icon, player_ids, referees, location)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    check_query = """
    SELECT 1 FROM game WHERE game_name = %s
    """
    cur.execute(check_query, (data["game_name"],))
    result = cur.fetchone()
    if result:
        print(f"Game {data['game_name']} already exists.")
    else:
        cur.execute(
        insert_query, 
            (
                data["game_name"],
                data["date"],
                data["video_url"],
                data["home_team_name"],
                data["away_team_name"],
                data["home_team_icon"],
                data["away_team_icon"],
                data["player_ids"],
                data["referees"],
                data["location"],
            )
        )
        print(f"Game {data['game_name']} inserted to database.")
    conn.commit()
    cur.close()