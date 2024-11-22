from fastapi import FastAPI, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from fastapi.responses import RedirectResponse
from datetime import datetime
import socket, uvicorn, sys, os, time, threading
from model import BettingInfoCreate, BettingInfoUpdate
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import get_db_connection
conn = get_db_connection()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get_root():
    return RedirectResponse(url="/docs")

betting_cache = {}
def update_betting_odds(game_id: int):
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute("""
        SELECT bet_side, bet_amount
        FROM betting_info
        WHERE game_id = %s
    """, (game_id,))
    data = dictcur.fetchall()

    if len(data) > 0:
        away_bets = 1 #prevent division by zero
        home_bets = 1
        edge = 0.005
        for item in data:
            if item["bet_side"] == "home":
                home_bets += item["bet_amount"]
            else:
                away_bets += item["bet_amount"]
        total_bets = away_bets + home_bets
        if total_bets == 0:
            return  
        home_odds = total_bets / home_bets
        away_odds = total_bets / away_bets
        home_odds = min(10, home_odds * (1 - edge))
        away_odds = min(10, away_odds * (1 - edge))
        betting_cache[game_id] = {
            "data": {"home_odds": home_odds, "away_odds": away_odds},
            "timestamp": time.time()
        }

def is_cache_valid(game_id: int) -> bool: 
    if game_id not in betting_cache:
        return False
    return time.time() - betting_cache[game_id]["timestamp"] < 5

@app.get("/betting_odd/{game_id}")
async def get_betting_odd(game_id: int=Path(..., ge=1)):
    if not is_cache_valid(game_id):
        update_betting_odds(game_id)
        print("not valid")
    
    if game_id not in betting_cache or betting_cache[game_id]["data"] is None:
        raise HTTPException(status_code=400, detail="No betting data found.")
    return betting_cache[game_id]["data"]

@app.post("/batting_item/")
async def create_item(item: BettingInfoCreate):
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute("""
        SELECT point
        FROM users
        WHERE username = %s
    """, (item.username,))
    user = dictcur.fetchone()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if user['point'] < item.bet_amount:
        raise HTTPException(status_code=400, detail="Insufficient points to place the bet.")
    dictcur.execute("""
        SELECT id
        FROM game
        WHERE id = %s
    """, (item.game_id,))
    result = dictcur.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Game not found.")
    dictcur.execute("""
        INSERT INTO betting_info (username, game_id, bet_amount, bet_side, end_time)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (username, game_id) DO NOTHING
    """, (item.username, item.game_id, item.bet_amount, item.bet_side, item.end_time))
    if dictcur.rowcount == 0:  
        raise HTTPException(status_code=400, detail="Betting record already exists.")
    conn.commit()
    return {"message": "Bet has been placed successfully."}

@app.put("/batting_item/")
async def update_item(item: BettingInfoUpdate):
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute("""
        SELECT point
        FROM users
        WHERE username = %s
    """, (item.username,))
    user = dictcur.fetchone()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if user['point'] < item.bet_amount:
        raise HTTPException(status_code=400, detail="Insufficient points to place the bet.")

    dictcur.execute("""
    UPDATE betting_info
    SET bet_amount = %s, bet_side = %s
    WHERE username = %s AND game_id = %s
    RETURNING *
    """, (item.bet_amount, item.bet_side, item.username, item.game_id))
    result = dictcur.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Betting record not found.")
    conn.commit()
    return {"message": "Bet has been updated successfully."}

@app.delete("/batting_item/{username}/{game_id}")
async def delete_item(username: str, game_id: int):
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute("""
        DELETE FROM betting_info
        WHERE username = %s
          AND game_id = %s
        RETURNING *
    """, (username, game_id))

    result = dictcur.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Betting record not found.")
    conn.commit()
    return {"message": "Bet has been deleted successfully."}

@app.get("/batting_item/{username}/{game_id}")
async def read_item(username: str, game_id: int):
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute("""
        SELECT *
        FROM betting_info
        WHERE username = %s
          AND game_id = %s
    """, (username, game_id))
    result = dictcur.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="No data found")
    return dict(result)

@app.get("/game_info")
async def read_item():
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute(
        "SELECT id, game_name, date, video_url, home_team_name, away_team_name, home_team_icon, away_team_icon, referees, location FROM game"
    )
    result = dictcur.fetchall()

    if not result:
        raise HTTPException(status_code=404, detail="Betting record not found.")
    return [dict(row) for row in result]


@app.get("/player_info/{game_id}")
async def read_item(game_id: int=Path(ge = 1)):
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute("""
        SELECT player_info.*
        FROM player_info 
        JOIN game ON player_info.id = ANY(game.player_ids)
        WHERE game.id = %s
    """, (game_id,))
    result = dictcur.fetchall() 

    if not result:
        raise HTTPException(status_code=404, detail="No data found")
    return [dict(row) for row in result]

@app.get("/game_events_near_time/{game_id}/{time}")
async def read_item(game_id: int = Path(..., ge=1), time: str = Path(description="Time in HH:MM:SS format")):
    try:
        input_time = datetime.strptime(time, "%H:%M:%S").time()  
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Please use HH:MM:SS.")
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute("""
        SELECT game_event.*, 
        player_info_batter.icon AS batter_icon, 
        player_info_pitcher.icon AS pitcher_icon
        FROM game_event
        LEFT JOIN player_info AS player_info_batter ON game_event.batter_name = player_info_batter.name
        LEFT JOIN player_info AS player_info_pitcher ON game_event.pitcher_name = player_info_pitcher.name
        WHERE game_id = %s AND inning_time = (SELECT MAX(inning_time) FROM game_event WHERE game_id = %s AND inning_time <= %s)
        ORDER BY game_event.batting_order;
        """, (game_id, game_id, input_time)
    )
    result = dictcur.fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="No data found with inning_time smaller than input time")
    return [dict(row) for row in result]

@app.get("/game_events_before_time/{game_id}/{time}")
async def read_item(game_id: int = Path(..., ge=1), time: str = Path(description="Time in HH:MM:SS format")):
    try:
        input_time = datetime.strptime(time, "%H:%M:%S").time() 
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Please use HH:MM:SS.")
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute("""
        SELECT game_event.*, 
        player_info_batter.icon AS batter_icon, 
        player_info_pitcher.icon AS pitcher_icon
        FROM game_event
        LEFT JOIN player_info AS player_info_batter ON game_event.batter_name = player_info_batter.name
        LEFT JOIN player_info AS player_info_pitcher ON game_event.pitcher_name = player_info_pitcher.name
        WHERE game_event.game_id = %s AND game_event.inning_time <= %s
        ORDER BY game_event.inning_time ASC, game_event.batting_order ASC;
        """, (game_id, input_time)
    )
    result = dictcur.fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="No data found with inning_time smaller than input time")
    return [dict(row) for row in result]

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)

#venv\Scripts\activate