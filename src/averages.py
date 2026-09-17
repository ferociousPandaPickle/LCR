import requests
import os
import sys
import time
from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()
league_api_key = os.getenv("LEAGUE_API_KEY")

## Instead of calling new TCP connections everytimes here we reuse same connection
session = requests.Session()

#SUPABASE DB stuff
db_url = os.environ["SUPABASE_URL"]
db_key = os.environ["SUPABASE_SECRET_KEY"]
start_supabase = create_client(db_url,db_key)


## For these averages we will just base them off of NA --> maybe later feature to add averages for all regions


def pull_matches(queue: str, division: str, tier: str, page: int):
    pull_matches_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/{queue}/{division}/{tier}?page={page}&api_key={league_api_key}"
    response_pull_matches = session.get(pull_matches_url)

    if (response_pull_matches.status_code != 200):
        print(f"⚠️ Request failed ({response_pull_matches.status_code}): {pull_matches_url}")
        return None

    data = response_pull_matches.json()

    all_puuids_in_page = []

    for entry in data:
        all_puuids_in_page.append(entry["puuid"])

    print(f"Status == Reached End of Page: {page}✅")
    return all_puuids_in_page


def collect_match_ids(puuid_list: list, batch_size: int, wait_time_batch:int):
    set_match_ids = set()
    for i in range(0, len(puuid_list), batch_size):
        puuid_batch = puuid_list[i:i+batch_size]
        
        for puuid in puuid_batch:
            get_match_id_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=100&api_key={league_api_key}"
            puuid_specific_match_ids = session.get(get_match_id_url)
            if puuid_specific_match_ids.status_code != 200:
                print(f"⚠️ Failed for puuid {puuid}: {puuid_specific_match_ids.status_code}")
                continue
            data = puuid_specific_match_ids.json()
            set_match_ids.update(data)
        batch_number = (i // batch_size) + 1
        print(f" Completed Batch: {batch_number} ✅")
        if i + batch_size < len(puuid_list):
            print(f"Waiting {wait_time_batch}s before next batch...")
            time.sleep(wait_time_batch)

    return set_match_ids



def main():
    queue = "RANKED_SOLO_5x5"
    tier = "I"
    division = "DIAMOND"
    page = 1
    batch_size = 90
    wait_time_batch = 120

    puuid_list = pull_matches(queue, division, tier, page)
    if (puuid_list is None):
        print(f"❌ Cannot Fetch List of Players in {queue} {division} {tier} {page}")
        sys.exit(1)
    # print(*player_page_puuid, sep="\n")

    # Using the list of player puuids from page it will give us 100 match ids per puuid in the list
    page_match_ids_set = collect_match_ids(puuid_list, batch_size, wait_time_batch)
    print(f"Total Match Ids: {len(page_match_ids_set)} ✅")


    ## Now when we go into each game like what we gonna do is like get new unique puuids 
    ## this way like we don't need to like go loop into pages and shit
    
    ## look at claude guide




    



if __name__ == "__main__":
    main()

