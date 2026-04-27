#المصدر من صنع -: كالو كودكس
from flask import Flask, jsonify, request
import requests
import json
import time

app = Flask(__name__)

ALLOWED_REGIONS = {
    "IND", "BR", "US", "SAC", "BD",
    "ID", "PK", "VN", "ME", "TH"
}

LEVELS = {
    "1": 0, "2": 48, "3": 202, "4": 544, "5": 1012, "6": 1844, "7": 2792, "8": 3800,
    "9": 4870, "10": 6004, "11": 7192, "12": 8448, "13": 9776, "14": 11140, "15": 12566,
    "16": 14060, "17": 15610, "18": 17224, "19": 18902, "20": 20632, "21": 22424,
    "22": 24728, "23": 26192, "24": 28166, "25": 30200, "26": 32294, "27": 34448,
    "28": 37804, "29": 41174, "30": 44870, "31": 48852, "32": 53334, "33": 58566,
    "34": 64096, "35": 69994, "36": 76460, "37": 83108, "38": 91128, "39": 99322,
    "40": 108092, "41": 120144, "42": 133266, "43": 147472, "44": 162760, "45": 179126,
    "46": 196572, "47": 215368, "48": 235516, "49": 257010, "50": 279860, "51": 304056,
    "52": 348318, "53": 394982, "54": 444044, "55": 495508, "56": 549364, "57": 633756,
    "58": 721744, "59": 813336, "60": 908522, "61": 1041438, "62": 1180352, "63": 1325256,
    "64": 1476184, "65": 1634300, "66": 1840946, "67": 2056594, "68": 2281242, "69": 2514880,
    "70": 2757530, "71": 3059506, "72": 3372284, "73": 3699456, "74": 4041030, "75": 4397020,
    "76": 4829104, "77": 5282204, "78": 5756304, "79": 6251404, "80": 6767504, "81": 7381324,
    "82": 8043154, "83": 8752952, "84": 9510808, "85": 10316638, "86": 11277190, "87": 12360748,
    "88": 13360304, "89": 14482858, "90": 15659418, "91": 17026708, "92": 18453688, "93": 19941280,
    "94": 21488570, "95": 23095858, "96": 24763138, "97": 26490138, "98": 28277708, "99": 30124996,
    "100": 32032284,
}

def format_num(num):
    try:
        return f"{int(num):,}"
    except:
        return str(num)

def get_exp_for_level(level):
    try:
        level_str = str(int(level))
        return LEVELS.get(level_str, 0)
    except:
        return 0

def calculate_level_progress(current_exp, current_level):
    try:
        current_level = int(current_level)
        if current_level >= 100:
            return {
                "current_level": 100,
                "current_exp": current_exp,
                "exp_for_current_level": LEVELS["100"],
                "exp_for_next_level": LEVELS["100"],
                "exp_needed": 0,
                "exp_needed_for_100": 0,
                "progress_percentage": 100
            }
        
        exp_for_current = get_exp_for_level(current_level)
        exp_for_next = get_exp_for_level(current_level + 1)
        exp_for_100 = get_exp_for_level(100)
        
        if exp_for_next == 0 or exp_for_current == 0:
            return None
        
        exp_needed = exp_for_next - current_exp
        exp_needed_for_100 = exp_for_100 - current_exp
        
        exp_in_current_level = current_exp - exp_for_current
        exp_range_for_level = exp_for_next - exp_for_current
        if exp_range_for_level > 0:
            progress_percentage = min(100, max(0, (exp_in_current_level / exp_range_for_level) * 100))
        else:
            progress_percentage = 0
        
        return {
            "current_level": current_level,
            "current_exp": current_exp,
            "exp_for_current_level": exp_for_current,
            "exp_for_next_level": exp_for_next,
            "exp_needed": exp_needed,
            "exp_needed_for_100": exp_needed_for_100,
            "progress_percentage": round(progress_percentage, 1)
        }
    except Exception as e:
        print(f"Error in calculate_level_progress: {e}")
        return None

def fetch_player_info(uid, region):
    if region not in ALLOWED_REGIONS:
        return {
            "success": False,
            "message": f"Invalid region. Supported: {', '.join(sorted(ALLOWED_REGIONS))}"
        }

    api_url = f"https://infoooooo-v6v5.vercel.app/accinfo?uid={uid}"
    max_retries = 2
    timeout = 30

    for attempt in range(max_retries + 1):
        try:
            response = requests.get(api_url, timeout=timeout)

            if response.status_code != 200:
                if 500 <= response.status_code < 600 and attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                return {
                    "success": False,
                    "message": f"API Server Error (HTTP {response.status_code})"
                }

            data = response.json()
            if not data or "basicInfo" not in data:
                return {
                    "success": False,
                    "message": "Invalid or empty response from API"
                }

            return {"success": True, "data": data}

        except requests.Timeout:
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            return {"success": False, "message": "API Timeout after multiple attempts"}

        except requests.RequestException as e:
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            return {"success": False, "message": f"Request failed: {str(e)}"}

        except json.JSONDecodeError:
            return {"success": False, "message": "Invalid JSON response from API"}

    return {"success": False, "message": "Unexpected error"}

@app.route('/')
def home():
    return jsonify({
        "success": True,
        "message": "Free Fire Level Info API (using original info API)",
        "usage": "/level?uid=<UID>&region=<REGION>",
        "supported_regions": sorted(ALLOWED_REGIONS),
        "endpoints": {
            "/level": "GET with uid and region query parameters",
            "/levels": "Get all level EXP requirements",
            "/level/<level_number>/exp": "Get EXP required for a specific level"
        },
        "credit": "@STAR_GMR"
    })

@app.route('/level')
def get_level_info():
    uid = request.args.get('uid')
    region = request.args.get('region')
    
    if not uid or not region:
        return jsonify({
            "success": False,
            "message": "Missing required query parameters: uid and region"
        })
    
    if region not in ALLOWED_REGIONS:
        return jsonify({
            "success": False,
            "message": f"Invalid region. Supported: {', '.join(sorted(ALLOWED_REGIONS))}"
        })
    
    player_data = fetch_player_info(uid, region)
    if not player_data["success"]:
        return jsonify({
            "success": False,
            "message": player_data["message"],
            "uid": uid,
            "region": region
        })
    
    data = player_data["data"]
    basic_info = data.get("basicInfo", {})
    nickname = basic_info.get("nickname", "Unknown")
    current_level = basic_info.get("level", 0)
    current_exp = basic_info.get("exp", 0)
    
    progress = calculate_level_progress(current_exp, current_level)
    if not progress:
        return jsonify({
            "success": False,
            "message": "Could not calculate level progress",
            "uid": uid,
            "nickname": nickname
        })
    
    return jsonify({
        "success": True,
        "uid": uid,
        "region": region,
        "nickname": nickname,
        "current_level": progress['current_level'],
        "current_exp": progress['current_exp'],
        "exp_for_current_level": progress['exp_for_current_level'],
        "exp_for_next_level": progress['exp_for_next_level'],
        "exp_needed": progress['exp_needed'],
        "exp_needed_for_100": progress['exp_needed_for_100'],
        "progress_percentage": progress['progress_percentage'],
        "level_100_exp": LEVELS["100"]
    })

@app.route('/levels')
def get_all_levels():
    return jsonify({
        "success": True,
        "total_levels": 100,
        "level_100_exp": LEVELS["100"],
        "levels": LEVELS,
        "formatted_levels": {k: format_num(v) for k, v in LEVELS.items()}
    })

@app.route('/level/<level_number>/exp')
def get_exp_for_level_api(level_number):
    try:
        level = int(level_number)
        if level < 1 or level > 100:
            return jsonify({
                "success": False,
                "message": "Level must be between 1 and 100"
            })
        
        exp = get_exp_for_level(level)
        return jsonify({
            "success": True,
            "level": level,
            "exp_required": exp,
            "formatted_exp": format_num(exp)
        })
        
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid level number"
        })

if __name__ == '__main__':
    app.run(debug=True)
