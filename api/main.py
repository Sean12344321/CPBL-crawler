from fastapi import FastAPI, Path, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from fastapi.responses import HTMLResponse
import socket, uvicorn
import sys, os
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
def check_date_valid(date_str: str):
    date = date_str.split('-')
    if len(date) != 3 or not date[0].isdigit() or not date[1].isdigit() or not date[2].isdigit():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid date format. Date must be in YYYY-MM-DD format."
        )
    if int(date[0]) < 1990 or int(date[0]) > 2024 or int(date[1]) < 1 or int(date[1]) > 12 or int(date[2]) < 1 or int(date[2]) > 31:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid date. Date must be between 1990-01-01 and 2024-12-31."
        )
    
@app.get("/")
async def get_root():
    # Open and read the HTML file content
    with open("api_test.html") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.get("/batting_info/{game_number}/{date}")
async def read_item(game_number: int=Path(ge = 1), date: str=Path(..., description="Date in YYYY-MM-DD format")):
    check_date_valid(date)
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute(
        "SELECT * FROM batting_info WHERE game_number = %s AND game_date = %s", 
        (game_number, date)
    )
    result = dictcur.fetchall()

    if not result:
        raise HTTPException(status_code=404, detail="No data found")
    return [dict(row) for row in result]

@app.get("/game_info/{game_id}")
async def read_item(game_id: int=Path(ge = 1)):
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute(
        "SELECT * FROM game WHERE id = %s", 
        (game_id,)
    )
    result = dictcur.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="No data found")
    return dict(result)

if __name__ == '__main__':
    ip_address = socket.gethostbyname(socket.gethostname())
    uvicorn.run(app, host=ip_address, port=8000)

@app.get("/player_info/{game_id}")
async def read_item(game_id: int=Path(ge = 1)):
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute(
        "SELECT player_ids FROM game WHERE id = %s", 
        (game_id,)
    )
    player_ids = dictcur.fetchone()['player_ids']
    dictcur.execute(
        "SELECT * FROM player_info WHERE id = ANY(%s)", 
        (player_ids,)
    )
    result = dictcur.fetchall()  # Get all players with the specified ids

    if not result:
        raise HTTPException(status_code=404, detail="No data found")
    return result
#netstat -ano | findstr :8000