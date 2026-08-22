import requests
import json
import os
from dotenv import load_dotenv

#loads env file
load_dotenv()

league_api_key = os.getenv("LEAGUE_API_KEY")

#The vlaues will come from Frontend web
gameName = input("What is your gameName: ")
tagLine = input("What is your tagLine: ")
#User will have dropdown to select region
region = "americas"


base_url = f"https://{region}.api.riotgames.com"
get_puuid_url = f"{base_url}/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?{league_api_key}"

response = requests.get(get_puuid_url)
response_dict = response.json()

#If you want more people using at once need to use a list buddy
puuid_stored = response_dict["puuid"]

# MASTERY TABLE SETUP
get_mastery_url = f"{base_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid_stored}?{league_api_key}"

# Push Mastery into DB




# MATCH HISTORY TABLE SETUP

#This is a List holding many strings
get_match_history_url = f"{base_url}/lol/match/v5/matches/by-puuid/{puuid_stored}/ids?start=0&count=99&{league_api_key}"



# This will be the async thingy we need to do for
get_match_details_url = f"{base_url}/lol/match/v5/matches/{get_match_history_url[0]}?{league_api_key}"

# Push Matches into DB



#All the above will be functions you run inside a main or smthing



#Use to like see nice print
# print(json.dumps(response_dict, indent=4, sort_keys=True))
