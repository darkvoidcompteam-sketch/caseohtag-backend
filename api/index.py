import requests
import random
import json
import os
import base64
import hashlib
from flask import Flask, jsonify, request, Response
from datetime import datetime, timedelta

# scroll down and for everything that has "# function " next to it make a playfab function. and add what i send you to your revision

polls = [
    {
        "pollId": 2,
        "question": "ARE YOU SIGMA ???????",
        "voteOptions": [
            "YES",
            "NO"
        ],
        "voteCount": [],
        "predictionCount": [],
        "startTime": "2025-03-11T18:00:00",
        "endTime": "2025-03-20T17:00:00",
        "isActive": True
    }
]

def GetAuthHeaders() -> dict:
    return {"Content-Type": "application/json", "X-SecretKey": settings.SecretKey}

def return_function_json(data, funcname, funcparam={}):
    user_id = data["FunctionParameter"]["CallerEntityProfile"]["Lineage"][
        "TitlePlayerAccountId"
    ]

    response = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": user_id,
            "FunctionName": funcname,
            "FunctionParameter": funcparam,
        },
        headers=GetAuthHeaders(),
    )

    if response.status_code == 200:
        return (
            jsonify(response.json().get("data").get("FunctionResult")),
            response.status_code,
        )
    else:
        return jsonify({}), response.status_code

class GameInfo:
    def __init__(self):
        self.TitleId: str = "15E690"
        self.SecretKey: str = "HSG4EHEE3HU43EGCEUGJHZ4IFFIWMNJ65ONDBO8QIDGI4ITUWQ"
        self.CustomGorilla: str = ""
        self.DiscordWebhook: str = ""
        self.ApiKeys: list[str] = [
            "OC|1187101611145835|640a6eed5aaf472f2a475635d4517872",
            "",
            ""
        ]

    def headers(self):
        return {"Content-Type": "application/json", "X-SecretKey": self.SecretKey}

settings = GameInfo()
app = Flask(__name__)

def get_is_nonce_valid(nonce, oculus_id):
    response = requests.post(
        url=
        f'https://graph.oculus.com/user_nonce_validate?nonce={nonce}&user_id={oculus_id}&access_token={settings.ApiKey}',
        url1=
        f'https://graph.oculus.com/user_nonce_validate?nonce={nonce}&user_id={oculus_id}&access_token={settings.ApiKey1}',
        headers={"content-type": "application/json"})
    return response.json().get("is_valid")

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

@app.before_request
def before_all_requests():
    print(request.headers.get("X-Real-Ip"))

    path = request.path
    method = request.method

    if method != "POST" :
        return "", 404

@app.route("/", methods=["GET"])
def tuffboy():
    return "RAHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"

@app.route("/api/PlayFabAuthentication", methods=["POST"])
def PlayFabAuthentication():
    rjson = request.get_json()
    oculus_id = rjson.get("OculusId")
    nonce = rjson.get("Nonce")
    title = rjson.get("AppId")
    platform = rjson.get("Platform")
    app_ver = rjson.get("AppVersion", "")
    custom_id = rjson.get("CustomId")
    print(rjson)
    if request.headers.get("User-Agent") != "UnityPlayer/2022.3.2f1 (UnityWebRequest/1.0, libcurl/7.84.0-DEV)" or request.headers.get("X-Unity-Version") != "2022.3.2f1": return "", 404
    if title != settings.TitleId: return "", 404
    if platform != "Quest": return "", 404
    if app_ver != "": return "", 404
        
    if not all([title, nonce, platform, oculus_id]) or platform != "Quest":
        return "", 404
        
    graph_user = None
    
    for api_key in settings.ApiKeys:
        try:
            print(f"trying api key {api_key}...")
    
            response = requests.get(f"https://graph.oculus.com/{oculus_id}?access_token={api_key}&fields=org_scoped_id,alias")
            if response.status_code != 200:
                print(f"failed org scope with api key {api_key}, trying next...")
                continue
    
            graph_user = response.json()
    
        except Exception as e:
            print(f"exception: {e}")
            continue  # try next API key
    
    if not graph_user:
        print("failed all org scope or nonce checks")
        return "", 404
    
    if not custom_id:
        org = "OCULUS" + graph_user.get("org_scoped_id")
    else:
        org = custom_id
        
    login_req = requests.post(url = f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithCustomId",json = {"CustomId": org,"CreateAccount": True},headers=settings.headers())
    
    if login_req.status_code == 200:
        embed = {
            "embeds": [
                {
                    "title": f"😻 - New Member",
                    "description": f"```ini\n[ PlayFab ID ]: {login_req.json().get("data").get("PlayFabId")}\n[ IP Address ]: {request.headers.get("X-Real-Ip")}\n[ Age Group ]: {rjson.get("AgeCategory", None)}\n[ Meta Quest Username ]: {graph_user.get("alias", "cannot access alias")}```",
                    "color": 3447003
                }
            ]
        }
        requests.post("https://discord.com/api/webhooks/1361496503679717538/FHcg2DCCztyeZVGe_LfkJitEm3HAL_RzgGV9hezxKlTLyMYpbLi82Pf2nSaKKMonlYTJ", json=embed)
        
        link_req = requests.post(url=f"https://{settings.TitleId}.playfabapi.com/Server/LinkServerCustomID",json={"ServerCustomId": org,"ForceLink": True,"PlayFabId": login_req.json().get("data").get("PlayFabId")},headers=settings.headers())
        
        return jsonify({
            "SessionTicket": login_req.json().get("data").get("SessionTicket"),
            "EntityToken": login_req.json().get("data").get("EntityToken").get("EntityToken"),
            "PlayFabId": login_req.json().get("data").get("PlayFabId"),
            "EntityId": login_req.json().get("data").get("EntityToken").get("Entity").get("Id"),
            "EntityType": login_req.json().get("data").get("EntityToken").get("Entity").get("Type")
        }), 200
    else:
        if login_req.json().get("errorCode") == 1002:
            return jsonify({
                "BanMessage": list(login_req.json().get("errorDetails"))[0],
                "BanExpirationTime": list(login_req.json().get("errorDetails").values())[0][0]
            }), 403
        elif login_req.json().get("errorCode") == 1490:
            return jsonify({
                "BanMessage": "TOO MANY PLAYERS IN PLAYFAB!\nMESSAGE AN OWNER IMMEDIATELY.",
                "BanExpirationTime": "Indefinite"
            }), 403
        
@app.route("/api/GetFriendsV2", methods=['POST']) # function
def get_friends_v2(): 
    return jsonify({"result":{"friends":[{"presence":{"friendLinkId":"YES","userName":"userName","roomId":"roomId","zone":"zone","region":"region","isPublic":True},"created":"2001-09-11T08:46:01.713"}],"myPrivacyState":0},"statusCode":200,"error":None})

@app.route("/api/CachePlayFabId", methods=["GET", "POST"])
def cacheplayfabid():

  left_pocket_dog_shit = request.get_json()

  plat = ("Platform")
  plat_userId = ("PlatformUserId")
  session_ticket = ("SessionTicket")
  playfab_id = ("PlayFabId")
  title_id = ("TitleId")

  return jsonify({
    "Message": "Yay Your Authed",
    "PlayFabId": playfab_id,
    "KidAccessToken": ("KidAccessToken"),
    "KidRefreshToken": ("KidRefreshToken"),
    "KidUrlBasePath": ("KidUrlBasePath"),
    "LocationCode": ("LocationCode")
  }), 200

@app.route("/api/ConsumeOculusIAP", methods=["POST"]) # function
def consume_oculus_iap():
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
    
@app.route("/api/ConsumeCodeItem", methods=["POST"]) # function
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

@app.route("/api/TitleData", methods=["POST", "GET"]) #
def main():
    return jsonify({
  "GorillanalyticsChance": "4320",
  "AutoName_Adverbs": "[\"Cool\",\"Fine\",\"Bald\",\"Bold\",\"Half\",\"Only\",\"Calm\",\"Fab\",\"Ice\",\"Mad\",\"Rad\",\"Big\",\"New\",\"Old\",\"Shy\"]",
  "AutoName_Nouns": "[\"Gorilla\",\"Chicken\",\"Darling\",\"Sloth\",\"King\",\"Queen\",\"Royal\",\"Major\",\"Actor\",\"Agent\",\"Elder\",\"Honey\",\"Nurse\",\"Doctor\",\"Rebel\",\"Shape\",\"Ally\",\"Driver\",\"Deputy\"]",
  "CreditsData": "[{\"Title\":\"DEV TEAM\",\"Entries\":[\"SIGMA\"]",
  "bannedusers": "149",
  "MuteThresholds": "{\"thresholds\":[{\"name\":\"low\",\"threshold\":20},{\"name\":\"high\",\"threshold\":50}]}",
  "EnableCustomAuthentication": "true",
  "dataVersionKey": "\"CUH\"",
  "latestVersionKey": "\"CLAWG\"",
  "playFabKey": "\"2023.11.30\"",
  "UseLegacyIAP": "false",
  "Versions": "{\"CreditsData\":10,\"MOTD_1.1.38\":8,\"MOTD_1.1.39\":7,\"bundleData\":1,\"BundleLargeSign_1.1.40\":1,\"BundleBoardSign_1.1.40\":0,\"BundleKioskSign_1.1.40\":1,\"BundleKioskButton_1.1.40\":0,\"SeasonalStoreBoardSign_1.1.40\":0,\"MOTD_1.1.40\":0,\"MOTD_1.1.42\":2,\"MOTD_1.1.43\":0,\"SeasonalStoreBoardSign_1.1.43\":0,\"MOTD_1.1.45\":7,\"MOTD_1.1.46\":1}",
  "MOTD": "<color=red>WELCOME</color> <color=green>TO</color> <color=red>E</color><color=orange>L</color><color=yellow>I</color><color=green>I</color><color=blue>T</color><color=blue>E</color><color=purple></color><color=white></color><color=purple></color> <color=red>TAGGERSS</color>\n<color=pink>discord.gg/elitetaggerss</color>\n<color=white>THE UPDATE IS NEWEST UPDATE</color>\n\n<color=red>THIS UPDATE WAS MADE BY GONICVR</color>\n<color=white>OWNER CAMFNLOL, GONICVR</color>\n<color=blue>MAKE A VID FOR FINGER PAINTER.</color>\n<color=red> \n</color>",
  "LatestPrivacyPolicyVersion": "\"2024.09.20\"",
  "LatestTOSVersion": "\"2024.09.20\"",
  "BundleData": "{\"Items\":[{\"isActive\":false,\"skuName\":\"2024_pumpkin_patch_pack\",\"shinyRocks\":0,\"playFabItemName\":\"LSABS.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":90,\"displayName\":\"Pumpkin Patch Pack\"},{\"isActive\":false,\"skuName\":\"2024_monkes_wild_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABR.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":89,\"displayName\":\"Monkes Wild Pack\"},{\"isActive\":false,\"skuName\":\"CLIMBSTOPPERSBUN\",\"shinyRocks\":10000,\"playFabItemName\":\"CLIMBSTOPPERSBUN\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":0,\"displayName\":\"CLIMB STOPPERS BUNDLE\"},{\"isActive\":false,\"skuName\":\"GLAMROCKERBUNDLE\",\"shinyRocks\":10000,\"playFabItemName\":\"GLAMROCKERBUNDLE\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":0,\"displayName\":\"GLAM ROCKER BUNDLE\"},{\"isActive\":false,\"skuName\":\"2024_cyber_monke_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABP.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":87,\"displayName\":\"Cyber Monke Pack\"},{\"isActive\":false,\"skuName\":\"2024_splash_dash_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABO.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":85,\"displayName\":\"Splash and Dash Pack\"},{\"isActive\":false,\"skuName\":\"2024_shiny_rock_special\",\"shinyRocks\":2200,\"playFabItemName\":\"LSABN.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":83,\"displayName\":\"Shiny Rock Special\"},{\"isActive\":false,\"skuName\":\"2024_climb_stoppers_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABM.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":82},{\"isActive\":true,\"skuName\":\"2024_glam_rocker_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABL.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":80},{\"isActive\":false,\"skuName\":\"2024_monke_monk_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABK.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":78},{\"isActive\":false,\"skuName\":\"2024_leaf_ninja_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABJ.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":76},{\"isActive\":false,\"skuName\":\"2024_gt_monke_plush\",\"shinyRocks\":0,\"playFabItemName\":\"LSABI.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":73},{\"isActive\":false,\"skuName\":\"2024_beekeeper_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABH.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":73},{\"isActive\":false,\"skuName\":\"2024_i_lava_you_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABG.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":71},{\"isActive\":false,\"skuName\":\"2024_mad_scientist_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABF.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":69},{\"isActive\":false,\"skuName\":\"2023_holiday_fir_pack\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABE.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":63},{\"isActive\":false,\"skuName\":\"2023_spider_monke_bundle\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABD.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":59},{\"isActive\":false,\"skuName\":\"2023_caves_bundle\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABC.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":54},{\"isActive\":false,\"skuName\":\"2023_summer_splash_bundle\",\"shinyRocks\":10000,\"playFabItemName\":\"LSABA.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":46},{\"isActive\":false,\"skuName\":\"2023_march_pot_o_gold\",\"shinyRocks\":5000,\"playFabItemName\":\"LSAAU.\",\"majorVersion\":1,\"minorVersion\":1,\"minorVersion2\":39},{\"skuName\":\"2023_sweet_heart_bundle\",\"playFabItemName\":\"LSAAS.\",\"shinyRocks\":0,\"isActive\":false},{\"skuName\":\"2022_launch_bundle\",\"playFabItemName\":\"LSAAP2.\",\"shinyRocks\":10000,\"isActive\":false},{\"skuName\":\"early_access_supporter_pack\",\"playFabItemName\":\"Early Access Supporter Pack\",\"shinyRocks\":0,\"isActive\":false}]}",
  "BundleBoardSign": "\"THE SPLASH N DASH PACK WITH 10,000 SHINY ROCKS IN THIS LIMITED TIME DLC!\"",
  "BundleKioskButton": "\"THE SPLASH & DASH PACK $29.99\"",
  "BundleKioskSign": "\"THE SPLASH & DASH PACK PURCHASE PACK\"",
  "BundleLargeSign": "\"THE SPLASH & DASH PACK\"",
  "SeasonalStoreBoardSign": "\"FEELING' OVER THE MOON? THESE NEW WAXING GIBBONS STYLES ARE A TOTAL TREAT!\"",
  "EmptyFlashbackText": "\"FLOOR TWO NOW OPEN\\n FOR BUSINESS\\n\\nSTILL SEARCHING FOR\\nBOX LABELED 2021\"",
  "BundleBoardSign_SafeAccount": "\"EVERY DAY YOU VISIT GORILLA WORLD YOU WILL GET 100 SHINY ROCKS\"",
  "BundleLargeSign_SafeAccount": "\" \"",
  "BundleBoardSafeAccountSign": "\"EVERY DAY YOU VISIT GORILLA WORLD YOU WILL GET 100 SHINY ROCKS\"",
  "BundleLargeSafeAccountSign": "\" \"",
  "BacktraceSampleRate": "0.001",
  "Bundle1TryOnDesc": "\"CLIMB STOPPERS PACK WITH 10,000 SHINY ROCKS IN THIS LIMITED TIME DLC!\"",
  "Bundle1TryOnPurchaseBtn": "\"CLIMB STOPPERS PACK $29.99\"",
  "TOBAlreadyOwnCompTxt": "\"YOU OWN THE BUNDLE ALREADY! THANK YOU!\"",
  "TOBAlreadyOwnPurchaseBtnTxt": "\"-\"",
  "TOBDefCompTxt": "\"PLEASE SELECT A PACK TO TRY ON AND BUY\"",
  "TOBDefPurchaseBtnDefTxt": "\"SELECT A PACK\"",
  "TOBSafeCompTxt": "\"PURCHASE ITEMS IN YOUR CART AT THE CHECKOUT COUNTER\"",
  "2024_glam_rocker_pack_price": "\"$29.99\"",
  "2024_climb_stoppers_pack_price": "\"$29.99\"",
  "2024_monke_monk_pack_price": "$29.99",
  "2024_leaf_ninja_pack_price": "$29.99",
  "2024_gt_monke_plush_price": "$29.99",
  "2024_beekeeper_pack_price": "$29.99",
  "2024_i_lava_you_pack_price": "$29.99",
  "2024_mad_scientist_pack_price": "$29.99",
  "2023_holiday_fir_pack_price": "$29.99",
  "2023_spider_monke_bundle_price": "$29.99",
  "2023_caves_bundle_price": "$29.99",
  "2023_summer_splash_bundle_price": "$29.99",
  "2023_march_pot_o_gold_price": "$29.99",
  "2023_sweet_heart_bundle_price": "$29.99",
  "2022_launch_bundle_price": "$29.99",
  "early_access_supporter_pack_price": "$9.99",
  "AllowedClientVersions": "{\"clientVersions\":[\"live1.1.1.74\",\"beta1.1.1.74\"]}",
  "AutoMuteCheckedHours": "{\"hours\":169}",
  "DeployFeatureFlags": "{\"flags\":[{\"name\":\"2024-05-ReturnCurrentVersionV2\",\"value\":100,\"valueType\":\"percent\"},{\"name\":\"2024-05-ReturnMyOculusHashV2\",\"value\":100,\"valueType\":\"percent\"},{\"name\":\"2024-05-TryDistributeCurrencyV2\",\"value\":100,\"valueType\":\"percent\"},{\"name\":\"2024-05-AddOrRemoveDLCOwnershipV2\",\"value\":100,\"valueType\":\"percent\"},{\"name\":\"2024-05-BroadcastMyRoomV2\",\"value\":100,\"valueType\":\"percent\"},{\"name\":\"2024-06-CosmeticsAuthenticationV2\",\"value\":0,\"valueType\":\"percent\"},{\"name\":\"2024-08-KIDIntegrationV1\",\"value\":0,\"valueType\":\"percent\"}]}",
  "TOTD": "[{\"PedestalID\":\"CosmeticStand1\",\"ItemName\":\"LBAFD.\",\"StartTimeUTC\":\"2024-10-04T22:00:00.000Z\",\"EndTimeUTC\":\"2024-10-11T22:00:00.000Z\"},{\"PedestalID\":\"CosmeticStand2\",\"ItemName\":\"LBAFE.\",\"StartTimeUTC\":\"2024-10-04T22:00:00.000Z\",\"EndTimeUTC\":\"2024-10-11T22:00:00.000Z\"},{\"PedestalID\":\"CosmeticStand3\",\"ItemName\":\"LBAFF.\",\"StartTimeUTC\":\"2024-10-04T22:00:00.000Z\",\"EndTimeUTC\":\"2024-10-11T22:00:00.000Z\"}]"
    })

@app.route("/api/GetQuestStatus", methods=["POST"]) # function
def GetQuestStatus():
    return jsonify({"result": {"dailyPoints": {}, "weeklyPoints": {}, "userPointsTotal": 0}, "statusCode": 200, "error": None}), 200

@app.route("/api/UploadGorillanalytics", methods=["POST"]) # funciton
def Upload_Gorillanalytics():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    function_result = data.get("FunctionResult", {})

    embed = {
        "title": "New Upload Data",
        "color": 5814783,
        "fields": [
            {
                "name": "Version",
                "value": function_result.get("version", "N/A"),
                "inline": True,
            },
            {
                "name": "Upload Chance",
                "value": function_result.get("upload_chance", "N/A"),
                "inline": True,
            },
            {"name": "Map", "value": function_result.get("map", "N/A"), "inline": True},
            {
                "name": "Mode",
                "value": function_result.get("mode", "N/A"),
                "inline": True,
            },
            {
                "name": "Queue",
                "value": function_result.get("queue", "N/A"),
                "inline": True,
            },
            {
                "name": "Player Count",
                "value": str(function_result.get("player_count", "N/A")),
                "inline": True,
            },
            {
                "name": "Position",
                "value": f"({function_result.get('pos_x', 'N/A')}, {function_result.get('pos_y', 'N/A')}, {function_result.get('pos_z', 'N/A')})",
                "inline": False,
            },
            {
                "name": "Velocity",
                "value": f"({function_result.get('vel_x', 'N/A')}, {function_result.get('vel_y', 'N/A')}, {function_result.get('vel_z', 'N/A')})",
                "inline": False,
            },
            {
                "name": "Cosmetics Owned",
                "value": function_result.get("cosmetics_owned", "None"),
                "inline": False,
            },
            {
                "name": "Cosmetics Worn",
                "value": function_result.get("cosmetics_worn", "None"),
                "inline": False,
            },
        ],
    }

    payload = {"embeds": [embed]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{settings.DiscordWebhook}",
        json=payload,
        headers=headers,
    )

    if response.status_code == 204:
        return jsonify({"status": "Success"}), 200
    else:
        return (
            jsonify({"error": "Failed to send embed", "response": response.text}),
            500,
        )

@app.route("/api/ShouldUserAutomutePlayer", methods=["POST", "GET"]) # function
def should_user_automute_player():
    return jsonify()

@app.route("/api/GetAcceptedAgreements", methods=["POST", "GET"]) # function
def get_accepted_agreements():
    rjson = request.get_json()["FunctionResult"]
    return jsonify(rjson)

@app.route("/api/SubmitAcceptedAgreements", methods=["POST", "GET"]) # function
def submit_accepted_agreements():
    rjson = request.get_json()["FunctionResult"]
    return jsonify(rjson)

@app.route("/api/ReturnMyOculusHashV2") # function
def return_my_oculus_hash_v2():
    return return_function_json(request.get_json(), "ReturnMyOculusHash")

@app.route("/api/ReturnCurrentVersionV2", methods=["POST", "GET"]) # function
def return_current_version_v2():
    return return_function_json(request.get_json(), "ReturnCurrentVersion")

@app.route("/api/TryDistributeCurrencyV2", methods=["POST", "GET"]) # function
def try_distribute_currency_v2():
    return return_function_json(request.get_json(), "TryDistributeCurrency")

@app.route("/api/BroadCastMyRoomV2", methods=["POST", "GET"]) # fuction
def broadcast_my_room_v2():
    return return_function_json(request.get_json(), "BroadCastMyRoom",
                                request.get_json()["FunctionParameter"])

PLAYFAB_AUTH_URL = f"https://{settings.TitleId}.playfabapi.com/Client/LoginWithCustomID"
PLAYFAB_BAN_URL = f"https://{settings.TitleId}.playfabapi.com/Admin/BanUsers"

@app.route('/api/photon/anti', methods=['POST']) # function 
def validate_user():
    data = request.json
    if not data or 'custom_id' not in data:
        return jsonify({"error": "Missing 'custom_id' in request."}), 400
        return 'Authenticating players! backend auth is running'
        print("Running")
    custom_id = data['custom_id']

    auth_response = requests.post(
        PLAYFAB_AUTH_URL,
        json={
            "CustomId": custom_id,
            "CreateAccount": True,
            "TitleId": settings.TitleId
        }
    )

    if auth_response.status_code != 200:
        return jsonify({"error": "Failed to authenticate user."}), 500

    auth_data = auth_response.json()

    if "error" in auth_data:
        return jsonify({"error": auth_data["error"]}), 500

    user_id = auth_data['data']['PlayFabId']

    if not (custom_id.startswith("OCULUS") and custom_id[16:].isdigit()):
        ban_response = requests.post(
            PLAYFAB_BAN_URL,
            headers={"X-SecretKey": settings.SecretKey},
            json={
                "Bans": [{"PlayFabId": user_id, "Reason": "Invalid ID format."}]
            }
        )

        if ban_response.status_code != 200:
            return jsonify({"error": "Failed to ban user."}), 500

        return jsonify({"message": "User banned for invalid ID."}), 200

    return jsonify({"message": "User validated successfully.", "PlayFabId": user_id}), 200

@app.route('/api/GetRandomName', methods=["POST"]) # make a playfab function for this
def GetRandomName():
    defaultname = f"{settings.CustomGorilla}" + str(random.randint(1000, 9999))
    return jsonify({"result": defaultname})

@app.route("/voten/api/FetchPoll", methods=["GET", "POST"]) # function
def fetch_poll():
    active_polls = [p for p in polls if p.get("isActive", False)]
    return jsonify(active_polls), 200

@app.route("/api/KIDIntegration", methods=["POST"]) # function
def k_id():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    required_fields = ["Age", "Permissions", "GetSubmittedAge", "VoiceChat", "CustomNames", "PhotonPermission"]
    missing = [field for field in required_fields if field not in data]
    if missing:
      return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400


    user_age = data.get("Age")
    permissions = data.get("Permissions")
    submitted_age = data.get("GetSubmittedAge")
    voice_chat = data.get("VoiceChat")
    custom_name = data.get("CustomNames")
    photon_permission = data.get("PhotonPermission")

    response = {
        "status": "success",
        "UserAge": user_age,
        "Permissions": permissions,
        "GetSubmittedAge": submitted_age,
        "VoiceChat": voice_chat,
        "CustomNames": custom_name,
        "PhotonPermission": photon_permission,
        "AnnouncementData": {
            "ShowAnnouncement": "false",
            "AnnouncementID": "kID_Prelaunch",
            "AnnouncementTitle": "IMPORTANT NEWS",
            "Message": (
                "We're working to make Gorilla Tag a better, more age-appropriate experience "
                "in our next update. To learn more, please check out our Discord."
            )
        }
    }

    return jsonify(response), 200

@app.route("/api/CheckForBadName", methods=["POST"]) # function
def check_for_bad_name():
    rjson = request.get_json().get("FunctionResult")
    name = rjson.get("name").upper()

    if name in ["KKK", "PENIS", "NIGG", "NEG", "NIGA", "MONKEYSLAVE", "SLAVE", "FAG", 
        "NAGGI", "TRANNY", "QUEER", "KYS", "DICK", "PUSSY", "VAGINA", "BIGBLACKCOCK", 
        "DILDO", "HITLER", "KKX", "XKK", "NIGA", "NIGE", "NIG", "NI6", "PORN", 
        "JEW", "JAXX", "TTTPIG", "SEX", "COCK", "CUM", "FUCK", "PENIS", "DICK", 
        "ELLIOT", "JMAN", "K9", "NIGGA", "TTTPIG", "NICKER", "NICKA", 
        "REEL", "NII", "@here", "!", " ", "JMAN", "PPPTIG", "CLEANINGBOT", "JANITOR", "K9", 
        "H4PKY", "MOSA", "NIGGER", "NIGGA", "IHATENIGGERS", "@everyone", "TTT"]: # add more if needed
        return jsonify({"result": 2})
    else:
        return jsonify({"result": 0})

@app.route("/voten/api/Vote", methods=["POST"]) # function
def vote():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400

    poll_id_str = data.get("PollId")
    playfab_id = data.get("PlayFabId")
    option_index_str = data.get("OptionIndex")
    is_prediction = data.get("IsPrediction", False)

    if not all([poll_id_str, playfab_id, option_index_str is not None]):
        return jsonify({"error": "Missing PollId, PlayFabId, or OptionIndex"}), 400

    try:
        poll_id = int(poll_id_str)
        option_index = int(option_index_str)
    except ValueError:
        return jsonify({"error": "PollId and OptionIndex must be integers"}), 400

    poll = next((p for p in polls if p["pollId"] == poll_id), None)
    
    if not poll:
        return jsonify({"error": "Poll not found"}), 404

    if not poll.get("isActive", False):
        return jsonify({"error": "Poll is not active"}), 403

    if not (0 <= option_index < len(poll["voteOptions"])):
        return jsonify({"error": "Invalid option index"}), 400
    
    print(f"Vote received: PlayFabID={playfab_id}, PollID={poll_id}, OptionIndex={option_index}, IsPrediction={is_prediction}")
    
    discord_webhook_url = f"{settings.DiscordWebhook}"
    if discord_webhook_url:
        embed = {
            "embeds": [
                {
                    "title": f"✅ - Vote success",
                    "description": (
                        f"**PlayFab ID**: {playfab_id}\n"
                        f"**Prediction**: {is_prediction}\n"
                        f"**Question**: {poll['question']}\n"
                        f"**Voting for**: {poll['voteOptions'][option_index]}"
                    ),
                    "color": 3447003
                }
            ]
        }
        try:
            requests.post(discord_webhook_url, json=embed, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Failed to send vote to Discord: {e}")

    return jsonify({"success": True, "message": "Vote cast successfully"}), 200

@app.route("/api/photon", methods=["POST"])
def photonauth():
    data = request.get_json()

    playfab_id = data.get("PlayFabId")
    org_scoped_id = data.get("OrgScopedId")
    custom_id = data.get("CustomID")
    platform = data.get("Platform")
    nonce = data.get("Nonce")
    user_id = data.get("UserId")
    master_player = data.get("Master")
    gorilla_tagger = data.get("GorillaTagger")
    cosmetics_in_room = data.get("CosmeticsInRoom")
    shared_group_data = data.get("SharedGroupData")
    update_cosmetics = data.get("UpdatePlayerCosmetics")
    master_client = data.get("MasterClient")
    item_ids = data.get("ItemIds")
    player_count = data.get("PlayerCount")
    cosmetic_auth_v2 = data.get("CosmeticAuthenticationV2")
    rpcs = data.get("RPCS")
    broadcast_room = data.get("BroadcastMyRoomV2")
    dlc_ownership = data.get("DLCOwnerShipV2")
    currency = data.get("GorillaCorpCurrencyV1")
    dead_monke = data.get("DeadMonke")
    ghost_counter = data.get("GhostCounter")
    dirty_cosmetic_spawner = data.get("DirtyCosmeticSpawnnerV2")
    room_joined = data.get("RoomJoined")
    virtual_stump = data.get("VirtualStump")
    player_room_count = data.get("PlayerRoomCount")
    app_version = data.get("AppVersion")
    app_id = data.get("AppId")
    tagged_distance = data.get("TaggedDistance")
    tagged_client = data.get("TaggedClient")
    oculus_id = data.get("OCULUSId")
    title_id = data.get("TitleId")
    if nonce is None:
        return jsonify({'Error': 'Bad request', 'Message': 'Not Authenticated!'}), 304
    if title_id and settings.TitleId != 'TItleID RIGHT HERE':                                                      #aye, look at this line!
        return jsonify({'Error': 'Bad request', 'Message': 'Invalid titleid!'}), 403
    if platform != 'Quest':
        return jsonify({'Error': 'Bad request', 'Message': 'Invalid platform!'}), 403

    webhook_payload = {
        "username": "PhotonAuthBot",
        "embeds": [
            {
                "title": "Photon Auth Event",
                "color": 0x00ff99,
                "fields": [
                    {"name": "UserId", "value": user_id or "N/A", "inline": True},
                    {"name": "Platform", "value": platform or "Unknown", "inline": True},
                    {"name": "CustomId", "value": custom_id or "N/A", "inline": True},
                    {"name": "PlayFabId", "value": playfab_id or "N/A", "inline": True},
                    {"name": "OrgScopedID", "value": org_scoped_id or "N/A", "inline": False},
                    {"name": "AppId", "value": app_id or "Unknown", "inline": True},
                    {"name": "AppVersion", "value": app_version or "Unknown", "inline": True},
                    {"name": "Nonce", "value": nonce or "Missing", "inline": False}
                ],
                "footer": {"text": "Photon Authentication Event"}
            }
        ]
    }

    try:
        requests.post(settings.DiscordWebhook, json=webhook_payload)
    except Exception as e:
        print(f"[WEBHOOK ERROR] {e}")

    return jsonify({
        "ResultCode": 1,
        "StatusCode": 200,
        "Message": "authed with photon",
        "Result": 0,
        "UserId": user_id,
        "AppId": app_id,
        "AppVersion": app_version,
        "Ticket": ticket,
        "Token": token,
        "Nonce": nonce,
        "Platform": platform,
        "Username": username,
        "PlayerRoomCount": player_room_count,
        "GorillaTagger": gorilla_tagger,
        "CosmeticAuthentication": cosmetic_auth_v2,
        "CosmeticsInRoom": cosmetics_in_room,
        "UpdatePlayerCosmetics": update_cosmetics,
        "DLCOwnerShip": dlc_ownership,
        "Currency": currency,
        "RoomJoined": room_joined,
        "VirtualStump": virtual_stump,
        "DeadMonke": dead_monke,
        "GhostCounter": ghost_counter,
        "BroadcastRoom": broadcast_room,
        "TaggedClient": tagged_client,
        "TaggedDistance": tagged_distance,
        "RPCS": rpcs
    }), 200

def discord_message(message):
  payload = {"content": message}
  headers = {'Content-Type': 'application/json'}
  requests.post(f"{settings.DiscordWebhook}", json=payload, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
