import requests
import os
import sys
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






def main():
    queue = "RANKED_SOLO_5x5"
    tier = "I"
    division = "DIAMOND"
    page = 1

    player_page_puuid = pull_matches(queue, division, tier, page)
    if (player_page_puuid is None):
        print(f"❌ Cannot Fetch List of Players in {queue} {division} {tier} {page}")
        sys.exit(1)
    # print(*player_page_puuid, sep="\n")

    

    



if __name__ == "__main__":
    main()

