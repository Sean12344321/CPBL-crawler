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
    
@app.get("/")
async def get_root():
    # Open and read the HTML file content
    with open("api_test.html") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.get("/game_info")
async def read_item():
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute(
        "SELECT * FROM game"
    )
    result = dictcur.fetchall()

    if not result:
        raise HTTPException(status_code=404, detail="No data found")
    standard_result = [dict(row) for row in result]
    return result


@app.get("/player_info/{game_id}")
async def read_item(game_id: int=Path(ge = 1)):
    dictcur = conn.cursor(cursor_factory=RealDictCursor)
    dictcur.execute(
        "SELECT player_ids FROM game WHERE id = %s", 
        (game_id,)
    )
    player_ids = dictcur.fetchone()['player_ids']
    dictcur.execute(
        "SELECT * FROM player_info WHERE id = ANY(%s::INTEGER[])", 
        (player_ids,) 
    )
    result = dictcur.fetchall()  # Get all players with the specified ids

    if not result:
        raise HTTPException(status_code=404, detail="No data found")
    standard_result = [dict(row) for row in result]
    print(len(standard_result))
    return standard_result

if __name__ == '__main__':
    ip_address = socket.gethostbyname(socket.gethostname())
    uvicorn.run(app, host=ip_address, port=8000)