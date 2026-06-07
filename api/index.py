import requests
import random
from flask import Flask, jsonify, request
import time

# hi! made in 40 minutes, enjoy! (or dont, idc)
# credits to: l1rson for some examples off his okay & shit backend.
# not made entirely from his backend but i did use some of his code for reference, so thanks l1rson!

class GameInfo:

    def __init__(self):
        self.TitleId: str = "15E690"
        self.SecretKey: str = "HSG4EHEE3HU43EGCEUGJHZ4IFFIWMNJ65ONDBO8QIDGI4ITUWQ"
        self.ApiKey: str = "640a6eed5aaf472f2a475635d4517872"
            "OC|1187101611145835|640a6eed5aaf472f2a475635d4517872"

    def get_auth_headers(self):
        return {
            "content-type": "application/json",
            "X-SecretKey": self.SecretKey
        }

settings = GameInfo()
app = Flask(__name__)
playfab_cache = {}
mute_cache = {}
used_nonces = {}
nonce_ttl = 300

settings.TitleId = ""
settings.SecretKey = ""
settings.ApiKey = ""

allowed_app_versions = ["1.0.0", "1.0.1", "1.1.0"]

# -------------------------------------------------
# -------------------------------------------------

# -------------------------------------------------
# -------------------------------------------------

def return_function_json(data, funcname, funcparam={}):
    user_id = data["FunctionParameter"]["CallerEntityProfile"]["Lineage"][
        "TitlePlayerAccountId"]

    response = requests.post(
        url=
        f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": user_id,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers=settings.get_auth_headers())

    if response.status_code == 200:
        return jsonify(response.json().get("data").get(
            "FunctionResult")), response.status_code
    else:
        return jsonify({}), response.status_code

def get_is_nonce_valid(nonce, oculus_id):
    response = requests.post(
        url=
        f'https://graph.oculus.com/user_nonce_validate?nonce={nonce}&user_id={oculus_id}&access_token={settings.ApiKey}',
        url1=
        f'https://graph.oculus.com/user_nonce_validate?nonce={nonce}&user_id={oculus_id}&access_token={settings.ApiKey1}',
        headers={"content-type": "application/json"})
    return response.json().get("is_valid")

def validation_failed(message="Meta account failed validation."):
    return jsonify({
        "Message": "Meta account failed validation."
    }), 403

def cleanup_nonces():
    now = time.time()
    expired = [n for n, t in used_nonces.items() if now - t > nonce_ttl]
    for n in expired:
        used_nonces.pop(n, None)

def validate(oculus_id, nonce):
    try:
        response = requests.post(
            "https://graph.oculus.com/user_nonce_validate",
            json={
                "access_token": settings.ApiKey,
                "nonce": nonce,
                "user_id": oculus_id
            },
            headers={"content-type": "application/json"},
            timeout=5
        )

        if response.status_code != 200:
            return False

        return response.json().get("is_valid", False)

    except requests.RequestException:
        return False

# -------------------------------------------------
# -------------------------------------------------

# -------------------------------------------------
# -------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def main():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>rickroll</title>
        <style>
            body {
                margin: 0;
                background: #0a0a0a;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                overflow: hidden;
            }

        .video-container {
            border-radius: 16px;
            overflow: hidden;
            box-shadow:
                0 0 8px rgba(0, 255, 255, 0.25),
                0 0 16px rgba(0, 255, 255, 0.15);
        }

            iframe {
                display: block;
                width: 960px;
                height: 540px;
                border: none;
            }
        </style>
    </head>
    <body>
        <div class="video-container">
            <iframe
                src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1"
                title="rickroll video player"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
        </div>
    </body>
    </html>
    """

# -------------------------------------------------
# -------------------------------------------------

# -------------------------------------------------
# -------------------------------------------------

@app.route("/api/PlayFabAuthentication", methods=["POST", "GET"])
def playfab_authentication():
    if request.method == "GET":
        return validation_failed()

    user_agent = request.headers.get("User-Agent", "")
    if "UnityPlayer" not in user_agent:
        return validation_failed()

    try:
        rjson = request.get_json(force=True, silent=True) or {}
    except Exception:
        return validation_failed()

    custom_id = rjson.get("CustomId")
    app_id = rjson.get("AppId")
    nonce = rjson.get("Nonce")
    oculus_id = rjson.get("OculusId")
    platform = rjson.get("Platform")
    app_version = rjson.get("AppVersion")

    if not custom_id or not custom_id.startswith("OCULUS"):
        return validation_failed()

    if not app_id or app_id != settings.TitleId:
        return jsonify({
            "Message": "Request sent for the wrong App ID",
            "Error": "BadRequest-AppIdMismatch",
        }), 400

    if not nonce or not oculus_id:
        return validation_failed()

    if platform != "Quest":
        return validation_failed()

    if not app_version or app_version == "-1" or app_version not in allowed_app_versions:
        return validation_failed("Outdated or invalid app version.")

    cleanup_nonces()
    if nonce in used_nonces:
        return validation_failed("Replay detected.")
    used_nonces[nonce] = time.time()

    try:
        nonce_response = requests.post(
            url="https://graph.oculus.com/user_nonce_validate",
            json={
                "access_token": settings.ApiKey,
                "nonce": nonce,
                "user_id": oculus_id
            },
            headers={"content-type": "application/json"},
            timeout=6
        )
        if nonce_response.status_code != 200:
            return validation_failed()
        if not nonce_response.json().get("is_valid", False):
            return validation_failed()
    except requests.exceptions.RequestException:
        return validation_failed("Oculus validation failed.")

    if not validate(oculus_id, nonce):
        return validation_failed()

    try:
        login_request = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithServerCustomId",
            json={
                "ServerCustomId": custom_id,
                "CreateAccount": True,
            },
            headers=settings.get_auth_headers(),
            timeout=8
        )
    except requests.exceptions.RequestException:
        return validation_failed("PlayFab unreachable.")

    if login_request.status_code == 200:
        data = login_request.json().get("data", {})
        entity = data.get("EntityToken", {})
        ent_obj = entity.get("Entity", {})

        return jsonify({
            "PlayFabId": data.get("PlayFabId"),
            "SessionTicket": data.get("SessionTicket"),
            "EntityToken": entity.get("EntityToken"),
            "EntityId": ent_obj.get("Id"),
            "EntityType": ent_obj.get("Type"),
        }), 200

    if login_request.status_code == 403:
        try:
            ban_info = login_request.json()
        except Exception:
            return validation_failed()

        if ban_info.get("errorCode") == 1002:
            ban_message = ban_info.get("errorMessage", "Your account has been traced and you have been banned.")
            ban_details = ban_info.get("errorDetails", {})
            ban_expiration_key = next(iter(ban_details.keys()), None)
            ban_expiration_list = ban_details.get(ban_expiration_key, [])
            ban_expiration = ban_expiration_list[0] if ban_expiration_list else "Indefinite"

            return jsonify({
                "BanMessage": ban_message,
                "BanExpirationTime": ban_expiration,
            }), 403

    return validation_failed(ban_info.get("errorMessage", "Meta account failed validation."))
# -------------------------------------------------
# -------------------------------------------------

# -------------------------------------------------
# -------------------------------------------------
@app.route("/api/CachePlayFabId", methods=["GET", "POST"])
def cacheplayfabid():

  right_pocket_cat_piss = request.get_json()

  plat = right_pocket_cat_piss.get("Platform")
  plat_userId = right_pocket_cat_piss.get("PlatformUserId")
  session_ticket = right_pocket_cat_piss.get("SessionTicket")
  playfab_id = right_pocket_cat_piss.get("PlayFabId")
  title_id = right_pocket_cat_piss.get("TitleId")

  return jsonify({
    "Message": "Hi Lol",
    "PlayFabId": playfab_id,
    "KidAccessToken": right_pocket_cat_piss.get("KidAccessToken"),
    "KidRefreshToken": right_pocket_cat_piss.get("KidRefreshToken"),
    "KidUrlBasePath": right_pocket_cat_piss.get("KidUrlBasePath"),
    "LocationCode": right_pocket_cat_piss.get("LocationCode")
  }), 200

# -------------------------------------------------
# -------------------------------------------------

# -------------------------------------------------
# -------------------------------------------------

@app.route("/api/ConsumeCodeItem", methods=["POST"])
def consume_code_item():
    rjson = request.get_json()
    code = rjson.get("itemGUID")
    playfab_id = rjson.get("playFabID")
    session_ticket = rjson.get("playFabSessionTicket")

    if not all([code, playfab_id, session_ticket]):
        return jsonify({"error": "Missing parameters"}), 400

    raw_url = f"" 
    response = requests.get(raw_url)

    if response.status_code != 200:
        return jsonify({"error": "GitHub fetch failed"}), 500

    lines = response.text.splitlines()
    codes = {split[0].strip(): split[1].strip() for line in lines if (split := line.split(":")) and len(split) == 2}

    if code not in codes:
        return jsonify({"result": "CodeInvalid"}), 404

    if codes[code] == "AlreadyRedeemed":
        return jsonify({"result": codes[code]}), 200

    grant_response = requests.post(
        f"https://{settings.TitleId}.playfabapi.com/Admin/GrantItemsToUsers",
        json={
            "ItemGrants": [
                {
                    "PlayFabId": playfab_id,
                    "ItemId": item_id,
                    "CatalogVersion": "DLC"
                } for item_id in ["dis da cosmetics", "anotehr cposmetic", "anotehr"]
            ]
        },
        headers=settings.get_auth_headers()
    )


    if grant_response.status_code != 200:
        return jsonify({"result": "PlayFabError", "errorMessage": grant_response.json().get("errorMessage", "Grant failed")}), 500

    new_lines = [f"{split[0].strip()}:AlreadyRedeemed" if split[0].strip() == code else line.strip() 
             for line in lines if (split := line.split(":")) and len(split) >= 2]

    updated_content = "\n".join(new_lines).strip()

    return jsonify({"result": "Success", "itemID": code, "playFabItemName": codes[code]}), 200

@app.route("/api/ConsumeOculusIAP", methods=["POST"])
def okay():
    rjson = request.get_json()

    access_token = rjson.get("userToken")
    user_id = rjson.get("userID")
    nonce = rjson.get("nonce")
    sku = rjson.get("sku")

    response = requests.post(
        url=
        f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={user_id}&sku={sku}&access_token={settings.ApiKey}",
        headers={"content-type": "application/json"})

    if response.json().get("success"):
        return jsonify({"result": True})
    else:
        return jsonify({"error": True})

# -------------------------------------------------
# -------------------------------------------------

# -------------------------------------------------
# -------------------------------------------------
    
@app.route("/api/CheckForBadName", methods=["POST", "GET"])
def checkforbadname():
    rjson = request.get_json() 
    function_result = rjson["FunctionArgument"]
    playfab_id = rjson["CallerEntityProfile"]["Lineage"]["MasterPlayerAccountId"]
    name = function_result["name"].upper()
    forRoom = function_result["forRoom"]

    if forRoom == True:
        return jsonify({"result": 0})

    link_response = requests.post(
        url=f"https://{settings.titleid}.playfabapi.com/Admin/UpdateUserTitleDisplayName",
        json={
            "DisplayName": name,
            "PlayFabId": playfab_id,
        },
        headers=settings.get_auth_headers(),
    ).json()
    return jsonify({"result": 0})

# -------------------------------------------------
# -------------------------------------------------

# -------------------------------------------------
# -------------------------------------------------

@app.route('/api/TitleData', methods=['POST', 'GET'])
def titledata():
    if request.method != "POST":
        return "", 404
    response_data = {
        "AutoMuteCheckedHours": {
            "hours": 169
        },
        "AutoName_Adverbs": [
            "Cool", "Fine", "Bald", "Bold", "Half", 
            "Only", "Calm", "Fab", "Ice", "Mad", 
            "Rad", "Big", "New", "Old", "Shy"
        ],
        "AutoName_Nouns": [
            "Gorilla", "Chicken", "Darling", "Sloth", "King", 
            "Queen", "Royal", "Major", "Actor", "Agent", 
            "Elder", "Honey", "Nurse", "Doctor", "Rebel", 
            "Shape", "Ally", "Driver", "Deputy"
        ],
        "BundleBoardSign": "<color=#73f0dd>MADE BY RAINS</color>",
        "BundleKioskButton": "<color=#73f0dd>MADE BY RAINS</color>",
        "BundleKioskSign": "<color=#73f0dd>MADE BY RAINS</color>",
        "BundleLargeSign": "<color=#73f0dd>MADE BY RAINS</color>",
        "EmptyFlashbackText": "FLOOR TWO NOW OPEN\n FOR BUSINESS\n\nSTILL SEARCHING FOR\nBOX LABELED 2021",
        "EnableCustomAuthentication": True,
        "GorillanalyticsChance": 4320,
        "LatestPrivacyPolicyVersion": "2024.09.20",
        "LatestTOSVersion": "2024.09.20",
        "MOTD": "<color=#73f0dd>WELCOME TO RAINS BACKEND, MADE IN 30 MINUTES!</color>",
        "SeasonalStoreBoardSign": "<color=#73f0dd>MADE BY RAINS</color>",
        "TOS_2024.09.20": "<color=#73f0dd>DISCORD.GG/</color>",
        "TOBAlreadyOwnCompTxt": "<color=#73f0dd>DISCORD.GG/</color>",
        "TOBAlreadyOwnPurchaseBundle": "BLABLABLA",
        "TOBDefCompTxt": "<color=#73f0dd>DISCORD.GG/</color>",
        "TOBDefPurchaseBtnDefTxt": "BLABLABLA",
        "UseLegacyIAP": False
        
    }
    return jsonify(response_data)

# -------------------------------------------------
# -------------------------------------------------

# -------------------------------------------------
# -------------------------------------------------


@app.route("/api/GetAcceptedAgreements", methods=["POST", "GET"])
def get_accepted_agreements():
    rjson = request.get_json()["FunctionResult"]
    return jsonify(rjson)

@app.route("/api/SubmitAcceptedAgreements", methods=["POST", "GET"])
def submit_accepted_agreements():
    rjson = request.get_json()["FunctionResult"]
    return jsonify(rjson)

@app.route("/api/ReturnMyOculusHashV2")
def return_my_oculus_hash_v2():
    return return_function_json(request.get_json(), "ReturnMyOculusHash")

@app.route("/api/ReturnCurrentVersionV2", methods=["POST", "GET"])
def return_current_version_v2():
    return return_function_json(request.get_json(), "ReturnCurrentVersion")

@app.route("/api/TryDistributeCurrencyV2", methods=["POST", "GET"])
def try_distribute_currency_v2():
    return return_function_json(request.get_json(), "TryDistributeCurrency")

@app.route("/api/BroadCastMyRoomV2", methods=["POST", "GET"])
def broadcast_my_room_v2():
    return return_function_json(request.get_json(), "BroadCastMyRoom",
                                request.get_json()["FunctionParameter"])

@app.route("/api/ShouldUserAutomutePlayer", methods=["POST", "GET"])
def should_user_automute_player():
    return jsonify(mute_cache)

@app.route('/api/GetName', methods=['POST', 'GET'])
def GetName():
    return jsonify({"result": f"GORILLA{random.randint(1000,9999)}"})

# -------------------------------------------------
# -------------------------------------------------

# -------------------------------------------------
# -------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

@app.route("/api/photon", methods=["POST"])
def photonauth():
    print(f"Received {request.method} request at /api/photon")
    getjson = request.get_json()
    Ticket = getjson.get("Ticket")
    Nonce = getjson.get("Nonce")
    Platform = getjson.get("Platform")
    UserId = getjson.get("UserId")
    nickName = getjson.get("username")
    if request.method.upper() == "GET":
        rjson = request.get_json()
        print(f"{request.method} : {rjson}")

        userId = Ticket.split('-')[0] if Ticket else None
        print(f"Extracted userId: {UserId}")

        if userId is None or len(userId) != 16:
            print("Invalid userId")
            return jsonify({
                'resultCode': 2,
                'message': 'Invalid token',
                'userId': None,
                'nickname': None
            })

        if Platform != 'Quest':
            return jsonify({'Error': 'Bad request', 'Message': 'Invalid platform - Good Try Blud!'}),403

        if Nonce is None:
            return jsonify({'Error': 'Bad request', 'Message': 'Still waiting for Authentication!'}),304

        req = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": userId},
            headers={
                "content-type": "application/json",
                "X-SecretKey": settings.SecretKey
            })

        print(f"Request to PlayFab returned status code: {req.status_code}")

        if req.status_code == 200:
            nickName = req.json().get("UserInfo",
                                      {}).get("UserAccountInfo",
                                              {}).get("Username")
            if not nickName:
                nickName = None

            print(
                f"Authenticated user {userId.lower()} with nickname: {nickName}"
            )

            return jsonify({
                'resultCode': 1,
                'message':
                f'Authenticated user {userId.lower()} title {settings.TitleId.lower()}',
                'userId': f'{userId.upper()}',
                'nickname': nickName
            })
        else:
            print("Failed to get user info from PlayFab")
            return jsonify({
                'resultCode': 0,
                'message': "Something went wrong",
                'userId': None,
                'nickname': None
            })

    elif request.method.upper() == "POST":
        rjson = request.get_json()
        print(f"{request.method} : {rjson}")

        ticket = rjson.get("Ticket")
        userId = ticket.split('-')[0] if ticket else None
        print(f"Extracted userId: {userId}")

        if userId is None or len(userId) != 16:
            print("Invalid userId")
            return jsonify({
                'resultCode': 2,
                'message': 'Invalid token',
                'userId': None,
                'nickname': None
            })

        req = requests.post(
             url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
             json={"PlayFabId": userId},
             headers={
                 "content-type": "application/json",
                 "X-SecretKey": settings.SecretKey
             })

        print(f"Authenticated user {userId.lower()}")
        print(f"Request to PlayFab returned status code: {req.status_code}")

        if req.status_code == 200:
             nickName = req.json().get("UserInfo",
                                       {}).get("UserAccountInfo",
                                               {}).get("Username")
             if not nickName:
                 nickName = None
             return jsonify({
                 'resultCode': 1,
                 'message':
                 f'Authenticated user {userId.lower()} title {settings.TitleId.lower()}',
                 'userId': f'{userId.upper()}',
                 'nickname': nickName
             })
        else:
             print("Failed to get user info from PlayFab")
             successJson = {
                 'resultCode': 0,
                 'message': "Something went wrong",
                 'userId': None,
                 'nickname': None
             }
             authPostData = {}
             for key, value in authPostData.items():
                 successJson[key] = value
             print(f"Returning successJson: {successJson}")
             return jsonify(successJson)
    else:
         print(f"Invalid method: {request.method.upper()}")
         return jsonify({
             "Message":
             "Use a POST or GET Method instead of " + request.method.upper()
         })
