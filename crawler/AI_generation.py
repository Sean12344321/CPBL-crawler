from dotenv import load_dotenv
import cohere, os

load_dotenv()
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
co2 = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY2"))
def summarize_game_details(pitches_count, game_details):
    system_message1 = """根據我提供的數字“壞球-好球”格式，生成:'投手總共投出X壞，Y好球。"""
    final_res = ""
    if pitches_count == "":
        pitches_count = "X-X"
    res = co.chat(
        model="command-r-plus-08-2024",  
        messages=[
            {"role": "system", "content": system_message1},
            {"role": "user", "content": pitches_count}, 
        ]
    )
    final_res += res.message.content[0].text 
    system_message2 = """你是一個播報棒球比賽的導播員，請根據投手每一球的打擊事實，用一句話簡短描述打手，投手的互動總結。請避免提及「結束半局」或其他描述換場的語句。"""
    game_details = "!!".join(game_details)
    if game_details == "":
        game_details = "這一球沒有打擊事實。"
    # Second API call for game details summary

    res = co2.chat(
        model="command-r-plus-08-2024",  
        messages=[
            {"role": "system", "content": system_message2},
            {"role": "user", "content": game_details},  
        ]
    )
    final_res += res.message.content[0].text 
    return final_res