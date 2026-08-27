import requests
import json
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime


###### REMMEMBER THIS IS  ONE PLAYER FUNCTIONALYIU NOT MORE THAN 1 CAN USE THIS AT ONCE OTHER BIG BANG WILL HAPPEN BOOM!

#loads env file
load_dotenv()

league_api_key = os.getenv("LEAGUE_API_KEY")

#The vlaues will come from Frontend web
gameName = input("What is your gameName: ")
tagLine = input("What is your tagLine: ")
#User will have dropdown to select region

base_url = f"https://na1.api.riotgames.com"


#SUPABASE DB stuff
db_url = os.getenv("SUPABASE_URL")
db_key = os.getenv("SUPABASE_SECRET_KEY")
start_supabase = create_client(db_url,db_key)



# PUUID STUFF
get_puuid_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={league_api_key}"
response_puuid = requests.get(get_puuid_url)
response_dict_puuid = response_puuid.json()
puuid_stored = response_dict_puuid["puuid"]


#Delete Prev info and rewrite new one
delete_table = (
    start_supabase.table("champion_mastery")
    .delete()
    .eq("puuid",puuid_stored)
    .execute()
)






# # # MASTERY TABLE SETUP
# get_mastery_url = f"{base_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid_stored}?api_key={league_api_key}"
# # #IT returns an object cannot print directly, so we use .json()
# response_mastery = requests.get(get_mastery_url)
# data_mastery = response_mastery.json()


# #Insert Mastery Values into DB FUNCTION
# # Uses Batch Insertion (fast)
# filtered_data_mastery = []
# for mastery in data_mastery:
#     if mastery["championPoints"] == 0:
#         continue
#     filtered_data_mastery.append(
#         {
#             "puuid": puuid_stored,
#             "champion_id": mastery["championId"],
#             "mastery_level": mastery["championLevel"],
#             "mastery_points": mastery["championPoints"],
#             "last_played": datetime.fromtimestamp(mastery["lastPlayTime"]/1000).isoformat()
#         }
#     )

# insert_mastery_db = start_supabase.table("champion_mastery").insert(filtered_data_mastery).execute()
# print("done")




# # # MATCH HISTORY TABLE SETUP

# # #This is a List holding many strings
# # # get_match_history_url = f"{base_url}/lol/match/v5/matches/by-puuid/{puuid_stored}/ids?start=0&count=99&{league_api_key}"



# # # This will be the async thingy we need to do for
# # # get_match_details_url = f"{base_url}/lol/match/v5/matches/{get_match_history_url[0]}?{league_api_key}"

# # # Push Matches into DB



# # #All the above will be functions you run inside a main or smthing



# # #Use to like see nice print
# # # print(json.dumps(response_dict, indent=4, sort_keys=True))
