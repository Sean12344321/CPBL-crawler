from fastapi import FastAPI, Path, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from fastapi.responses import RedirectResponse, StreamingResponse
from datetime import datetime
import uvicorn, sys, os, asyncio, json
from typing import Dict
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
betting_odds_cache: Dict[int, Dict] = {}

@app.get("/")
async def get_root():
    return RedirectResponse(url="/docs")

def get_betting_odds(game_id: int):
    print(f"update betting odds for {game_id}")
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute("""
        SELECT bet_side, bet_amount
        FROM betting_info
        WHERE game_id = %s
        AND settled = FALSE
    """, (game_id,))
    data = dictcur.fetchall()

    away_bets = 0 
    home_bets = 0
    for item in data:
        if item["bet_side"] == "home":
            home_bets += item["bet_amount"]
        else:
            away_bets += item["bet_amount"]
    total_bets = home_bets + away_bets
    if(total_bets == 0):
        return {"home": 0, "away": 0, "home_rate": 0, "away_rate": 0}
    home_rate = 10 if home_bets == 0 else min(10, total_bets / home_bets)
    away_rate = 10 if away_bets == 0 else min(10, total_bets / away_bets)
    return {"home": home_bets, "away": away_bets, "home_rate": home_rate, "away_rate": away_rate}

@app.get("/sse-betting-odds/{game_id}")
async def sse_betting_odds(game_id: int, request: Request):
    """
    Stream betting odds for a specific game_id to the frontend using SSE.
    """
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break # Stop sending events if the client disconnects
            current_data = betting_odds_cache.get(game_id)
            yield f"data: {json.dumps(current_data)}\n\n"
            await asyncio.sleep(1)  
    return StreamingResponse(event_generator(), media_type="text/event-stream")

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
        INSERT INTO betting_info (username, game_id, bet_amount, bet_side, end_time, settled)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (username, game_id) DO NOTHING
    """, (item.username, item.game_id, item.bet_amount, item.bet_side, item.end_time, False))

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
    if result["settled"]:
        raise HTTPException(status_code=400, detail="Betting record has already been settled.")
    conn.commit()
    return {"message": "Bet has been updated successfully."}

@app.delete("/batting_item")
async def delete_all_items():
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute("""DELETE FROM betting_info""")
    conn.commit()
    return {"message": "All bets have been deleted successfully."}

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
    if result["settled"]:
        raise HTTPException(status_code=400, detail="Betting record has already been settled.")
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

def settle_and_update_points():
    """
    Settle records and update user points based on betting outcomes.
    """
    dictcur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Step 1: Find unsettled records and calculate totals for each betting side
        query_unsettled = """
            SELECT
                bet_side,
                SUM(bet_amount) AS total_bet
            FROM betting_info
            WHERE end_time < %s
            AND settled = FALSE
            GROUP BY bet_side;
        """
        dictcur.execute(query_unsettled, (datetime.now(),))
        totals = dictcur.fetchall()
        # Calculate the total bets on home and away
        total_home = next((row['total_bet'] for row in totals if row['bet_side'] == 'home'), 0)
        total_away = next((row['total_bet'] for row in totals if row['bet_side'] == 'away'), 0)

        if total_home + total_away == 0:
            print("No bets to settle.")
            return

        # Calculate betting rates
        total_bets = total_home + total_away
        home_rate = 10 if total_home == 0 else min(10, total_bets / total_home)
        away_rate = 10 if total_away == 0 else min(10, total_bets / total_away)

        # Step 2: Update user points based on their bets
        query_user_update = """
            UPDATE users
            SET point = point + COALESCE((
                SELECT CASE 
                    WHEN bet_side = 'away' THEN bet_amount * (%(away_rate)s - 1)
                    ELSE -bet_amount
                END
                FROM betting_info
                WHERE betting_info.username = users.username
                AND betting_info.settled = FALSE
                AND betting_info.end_time < %(time)s
            ), 0)
            WHERE EXISTS (
                SELECT 1
                FROM betting_info
                WHERE betting_info.username = users.username
                AND betting_info.settled = FALSE
                AND betting_info.end_time < %(time)s
            );
        """
        dictcur.execute(query_user_update, {"home_rate": home_rate, "away_rate": away_rate, "time": datetime.now()})

        # Step 3: Mark records as settled
        query_update_settled = """
            UPDATE betting_info
            SET settled = TRUE
            WHERE end_time < %s
            AND settled = FALSE;
        """
        dictcur.execute(query_update_settled, (datetime.now(),))

        conn.commit()
        print(f"Settled records and updated user points at {datetime.now()}.")

    except Exception as e:
        print(f"Error settling records or updating points: {e}")
        
async def update_betting_odds():
    while True:
        global betting_odds_cache
        active_game_ids = [1]  
        for game_id in active_game_ids:
            betting_odds_cache[game_id] = get_betting_odds(game_id)
        await asyncio.sleep(1)

async def periodic_settled_update():
    """
    Periodically update settled records every 10 seconds.
    """
    while True:
        settle_and_update_points()
        await asyncio.sleep(10)  # Wait 10 seconds

@app.on_event("startup")
async def startup_event():
    """
    Start the periodic task on server startup.
    """
    asyncio.create_task(periodic_settled_update())
    asyncio.create_task(update_betting_odds())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)

#venv\Scripts\activate