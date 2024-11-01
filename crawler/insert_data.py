import json, os

def insert_broadcast_data(conn):
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