import json, os, sys
from psycopg2.extras import DictCursor
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import get_db_connection

conn = get_db_connection()

def insert_broadcast_data(data):
    cur = conn.cursor()
    insert_query = """
        INSERT INTO game_event (
            game_id, inning_time, inning_name, batter_name, pitcher_name,
            batting_details, batting_result, batting_number, batting_order, current_score, pitches_count
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    check_query = """
        SELECT 1 FROM game_event WHERE game_id = %s
    """
    
    cur.execute(check_query, (data[0]["game_id"],))
    result = cur.fetchone()
    if result:
        print(f"game_event for game {data[0]["game_id"]} already exists.")
    else :
        for record in data:
            cur.execute(insert_query, (
                record["game_id"],
                record["inning_time"],
                record["inning_name"],
                record["batter_name"],
                record["pitcher_name"],
                record["batting_details"],
                record["batting_result"],   
                record["batting_number"],
                record["batting_order"],
                record["current_score"],
                record["pitches_count"]
            ))
        print(f"game_event for game {data[0]["game_id"]} inserted to database.")
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

def update_broadcast_data(data):
    try:
        cur = conn.cursor()
        update_query = """
        UPDATE game_event
        SET pitches_count = %s
        WHERE batting_details = %s 
        AND inning_name = %s
        AND pitcher_name = %s
        """
        for record in data:
            cur.execute(
                update_query, (
                    record["pitches_count"],
                    record["batting_details"],
                    record["inning_name"],
                    record["pitcher_name"]
                )
            )
            print(record["pitches_count"])
            print(record["batting_details"])
            print(record["inning_name"])
            print("==================================")
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()