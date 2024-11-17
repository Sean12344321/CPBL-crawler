from fastapi import FastAPI, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from fastapi.responses import HTMLResponse
from datetime import datetime
import socket, uvicorn, sys, os
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
    # Open and read the HTML file content
    with open("api_test.html") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.get("/get_game_info")
async def read_item():
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute(
        "SELECT id, game_name, date, video_url, home_team_name, away_team_name, home_team_icon, away_team_icon, referees, location FROM game"
    )
    result = dictcur.fetchall()

    if not result:
        raise HTTPException(status_code=404, detail="No data found")
    return [dict(row) for row in result]


@app.get("/get_player_info/{game_id}")
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

@app.get("/get_game_events_near_time/{game_id}/{time}")
async def read_item(game_id: int = Path(..., ge=1), time: str = Path(...)):
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

@app.get("/get_game_events_before_time/{game_id}/{time}")
async def read_item(game_id: int = Path(..., ge=1), time: str = Path(...)):
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

if __name__ == '__main__':
    ip_address = socket.gethostbyname(socket.gethostname())
    uvicorn.run(app, host=ip_address, port=8000)