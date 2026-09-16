import requests
import os
import sys
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime


###### REMMEMBER THIS IS  ONE PLAYER FUNCTIONALYIU NOT MORE THAN 1 CAN USE THIS AT ONCE OTHER BIG BANG WILL HAPPEN BOOM!

#loads env file
load_dotenv()

league_api_key = os.getenv("LEAGUE_API_KEY")


#User will have dropdown to select region (in the frontend)

PLATFORMS = ["na1", "br1", "la1", "la2", "kr", "jp1", "euw1", "eun1", "tr1", "ru", "oc1", "ph2", "sg2", "th2", "tw2", "vn2"]

REGION_ROUTING = {
    # AMERICAS
    "na1": "americas",
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    # ASIA
    "kr": "asia",
    "jp1": "asia",
    # EUROPE
    "euw1": "europe",
    "eun1": "europe",
    "tr1": "europe",
    "ru": "europe",
    # SEA
    "oc1": "sea",
    "ph2": "sea",
    "sg2": "sea",
    "th2": "sea",
    "tw2": "sea",
    "vn2": "sea",
}

def get_urls(platform: str):
    platform = platform.lower()
    if platform not in REGION_ROUTING:
        raise ValueError(f"Unknown platform: {platform}")
    routing = REGION_ROUTING[platform]
    return {
        "base_url": f"https://{platform}.api.riotgames.com",   # for champion-mastery, league-v4, etc.
        "match_url": f"https://{routing}.api.riotgames.com",   # for match-v5, account-v1
    }

## Instead of calling new TCP connections everytimes here we reuse same connection
session = requests.Session()

#SUPABASE DB stuff
db_url = os.environ["SUPABASE_URL"]
db_key = os.environ["SUPABASE_SECRET_KEY"]
start_supabase = create_client(db_url,db_key)

# GET PUUID METHOD
def get_player_puuid(gameName:str, tagLine:str, match_url: str):
    get_puuid_url = f"{match_url}/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={league_api_key}"
    response_puuid = session.get(get_puuid_url)

    if(response_puuid.status_code != 200):
        print(f"⚠️ Request failed ({response_puuid.status_code}): {get_puuid_url}")
        return None

    response_dict_puuid = response_puuid.json()
    print("Status == Player PUUID ✅")
    return response_dict_puuid["puuid"]

def clear_puuid_specific_olddata(puuid_stored:str):
    #Deletes only Puuid Specific Data
    tables_to_delete = ["champion_mastery", "match_history"]
    for table in tables_to_delete:

        table_response = (
            start_supabase.table(table).delete().eq("puuid", puuid_stored).execute()
        )
        print(f"Status == Cleared old {table} ✅")


#### Champion Mastery
def get_player_champions_mastery(puuid_stored:str, base_url:str):
    get_mastery_url = f"{base_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid_stored}?api_key={league_api_key}"
    # #IT returns an object cannot print directly, so we use .json()
    response_mastery = session.get(get_mastery_url)
    print("Status == Player Champions_Mastery: retrieved total list ✅")
    return response_mastery.json()


def insert_only_played_mastery(puuid_stored:str, data_mastery:dict):
    #Insert Mastery Values into DB FUNCTION
    # Uses Batch Insertion (fast)
    filtered_data_mastery = []
    for mastery in data_mastery:
        if mastery["championPoints"] == 0:
            continue
        filtered_data_mastery.append(
            {
                "puuid": puuid_stored,
                "champion_id": mastery["championId"],
                "mastery_level": mastery["championLevel"],
                "mastery_points": mastery["championPoints"],
                "last_played": datetime.fromtimestamp(mastery["lastPlayTime"]/1000).isoformat()
            }
        )

    insert_mastery_db = start_supabase.table("champion_mastery").insert(filtered_data_mastery).execute()
    print("Status == Player Champions_Mastery: Insertion of only played_champions ✅")


#### Match History
def get_match_list(puuid_stored: str, match_count: int, queue_id: int, match_url:str):
    get_match_history_url = f"{match_url}/lol/match/v5/matches/by-puuid/{puuid_stored}/ids?queue={queue_id}&start=0&count={match_count}&api_key={league_api_key}"
    match_list_response = session.get(get_match_history_url)
    print(f"Status == Player Match List ✅")
    return match_list_response.json()


def extract_player_stats(player_index: int, participant: dict, match_id: str, puuid: str):
    challenges = participant.get("challenges", {})

    return {
        "match_id": match_id,
        "puuid": puuid,
        "riotIdGameName": participant.get("riotIdGameName"),
        "riotIdTagline": participant.get("riotIdTagline"),
        "championName": participant.get("championName"),
        "championId": participant.get("championId"),
        "championTransform": participant.get("championTransform", 0),
        "champLevel": participant.get("champLevel", 0),
        "champExperience": participant.get("champExperience", 0),
        "profileIcon": participant.get("profileIcon", 0),
        "teamId": participant.get("teamId"),
        "teamPosition": participant.get("teamPosition"),
        "individualPosition": participant.get("individualPosition"),
        "participantId": participant.get("participantId"),
        "subteamPlacement": participant.get("subteamPlacement", 0),
        "win": participant.get("win", False),

        # pings
        "allInPings": participant.get("allInPings", 0),
        "assistMePings": participant.get("assistMePings", 0),
        "basicPings": participant.get("basicPings", 0),
        "commandPings": participant.get("commandPings", 0),
        "dangerPings": participant.get("dangerPings", 0),
        "enemyMissingPings": participant.get("enemyMissingPings", 0),
        "enemyVisionPings": participant.get("enemyVisionPings", 0),
        "getBackPings": participant.get("getBackPings", 0),
        "holdPings": participant.get("holdPings", 0),
        "needVisionPings": participant.get("needVisionPings", 0),
        "onMyWayPings": participant.get("onMyWayPings", 0),
        "pushPings": participant.get("pushPings", 0),
        "retreatPings": participant.get("retreatPings", 0),
        "visionClearedPings": participant.get("visionClearedPings", 0),

        # core combat
        "assists": participant.get("assists", 0),
        "baronKills": participant.get("baronKills", 0),
        "deaths": participant.get("deaths", 0),
        "kills": participant.get("kills", 0),
        "killingSprees": participant.get("killingSprees", 0),
        "largestCriticalStrike": participant.get("largestCriticalStrike", 0),
        "largestKillingSpree": participant.get("largestKillingSpree", 0),
        "largestMultiKill": participant.get("largestMultiKill", 0),
        "doubleKills": participant.get("doubleKills", 0),
        "tripleKills": participant.get("tripleKills", 0),
        "quadraKills": participant.get("quadraKills", 0),
        "pentaKills": participant.get("pentaKills", 0),
        "unrealKills": participant.get("unrealKills", 0),

        # damage
        "damageDealtToBuildings": participant.get("damageDealtToBuildings", 0),
        "damageDealtToEpicMonsters": participant.get("damageDealtToEpicMonsters", 0),
        "damageDealtToObjectives": participant.get("damageDealtToObjectives", 0),
        "damageDealtToTurrets": participant.get("damageDealtToTurrets", 0),
        "damageSelfMitigated": participant.get("damageSelfMitigated", 0),
        "magicDamageDealt": participant.get("magicDamageDealt", 0),
        "magicDamageDealtToChampions": participant.get("magicDamageDealtToChampions", 0),
        "magicDamageTaken": participant.get("magicDamageTaken", 0),
        "physicalDamageDealt": participant.get("physicalDamageDealt", 0),
        "physicalDamageDealtToChampions": participant.get("physicalDamageDealtToChampions", 0),
        "physicalDamageTaken": participant.get("physicalDamageTaken", 0),
        "totalDamageDealt": participant.get("totalDamageDealt", 0),
        "totalDamageDealtToChampions": participant.get("totalDamageDealtToChampions", 0),
        "totalDamageShieldedOnTeammates": participant.get("totalDamageShieldedOnTeammates", 0),
        "totalDamageTaken": participant.get("totalDamageTaken", 0),
        "trueDamageDealt": participant.get("trueDamageDealt", 0),
        "trueDamageDealtToChampions": participant.get("trueDamageDealtToChampions", 0),
        "trueDamageTaken": participant.get("trueDamageTaken", 0),

        # gold / items
        "goldEarned": participant.get("goldEarned", 0),
        "goldSpent": participant.get("goldSpent", 0),
        "item0": participant.get("item0", 0),
        "item1": participant.get("item1", 0),
        "item2": participant.get("item2", 0),
        "item3": participant.get("item3", 0),
        "item4": participant.get("item4", 0),
        "item5": participant.get("item5", 0),
        "item6": participant.get("item6", 0),
        "itemsPurchased": participant.get("itemsPurchased", 0),
        "roleBoundItem": participant.get("roleBoundItem", 0),

        # objectives / structures
        "dragonKills": participant.get("dragonKills", 0),
        "inhibitorKills": participant.get("inhibitorKills", 0),
        "inhibitorTakedowns": participant.get("inhibitorTakedowns", 0),
        "inhibitorsLost": participant.get("inhibitorsLost", 0),
        "nexusKills": participant.get("nexusKills", 0),
        "nexusLost": participant.get("nexusLost", 0),
        "nexusTakedowns": participant.get("nexusTakedowns", 0),
        "objectivesStolen": participant.get("objectivesStolen", 0),
        "objectivesStolenAssists": participant.get("objectivesStolenAssists", 0),
        "turretKills": participant.get("turretKills", 0),
        "turretTakedowns": participant.get("turretTakedowns", 0),
        "turretsLost": participant.get("turretsLost", 0),

        # vision / wards
        "detectorWardsPlaced": participant.get("detectorWardsPlaced", 0),
        "sightWardsBoughtInGame": participant.get("sightWardsBoughtInGame", 0),
        "visionScore": participant.get("visionScore", 0),
        "visionWardsBoughtInGame": participant.get("visionWardsBoughtInGame", 0),
        "wardsKilled": participant.get("wardsKilled", 0),
        "wardsPlaced": participant.get("wardsPlaced", 0),

        # cc
        "timeCCingOthers": participant.get("timeCCingOthers", 0),
        "totalTimeCCDealt": participant.get("totalTimeCCDealt", 0),

        # minions / jungle (cs, cs_per_min are DB-generated — never insert these)
        "neutralMinionsKilled": participant.get("neutralMinionsKilled", 0),
        "totalMinionsKilled": participant.get("totalMinionsKilled", 0),
        "totalAllyJungleMinionsKilled": participant.get("totalAllyJungleMinionsKilled", 0),
        "totalEnemyJungleMinionsKilled": participant.get("totalEnemyJungleMinionsKilled", 0),

        # time / healing
        "timePlayed": participant.get("timePlayed", 0),
        "longestTimeSpentLiving": participant.get("longestTimeSpentLiving", 0),
        "totalHeal": participant.get("totalHeal", 0),
        "totalHealsOnTeammates": participant.get("totalHealsOnTeammates", 0),
        "totalTimeSpentDead": participant.get("totalTimeSpentDead", 0),
        "totalUnitsHealed": participant.get("totalUnitsHealed", 0),

        # summoner spells
        "spell1Casts": participant.get("spell1Casts", 0),
        "spell2Casts": participant.get("spell2Casts", 0),
        "spell3Casts": participant.get("spell3Casts", 0),
        "spell4Casts": participant.get("spell4Casts", 0),
        "summoner1Casts": participant.get("summoner1Casts", 0),
        "summoner1Id": participant.get("summoner1Id", 0),
        "summoner2Casts": participant.get("summoner2Casts", 0),
        "summoner2Id": participant.get("summoner2Id", 0),

        # booleans / flags
        "firstBloodAssist": participant.get("firstBloodAssist", False),
        "firstBloodKill": participant.get("firstBloodKill", False),
        "firstTowerAssist": participant.get("firstTowerAssist", False),
        "firstTowerKill": participant.get("firstTowerKill", False),
        "gameEndedInEarlySurrender": participant.get("gameEndedInEarlySurrender", False),
        "gameEndedInIGNBSurrender": participant.get("gameEndedInIGNBSurrender", False),
        "gameEndedInSurrender": participant.get("gameEndedInSurrender", False),
        "teamEarlySurrendered": participant.get("teamEarlySurrendered", False),
        "teamIGNBSurrendered": participant.get("teamIGNBSurrendered", False),

        # --- flattened from challenges, not nested (all numeric now, no wrapping needed) ---
        "abilityUses": challenges.get("abilityUses", 0),
        "acesBefore15Minutes": challenges.get("acesBefore15Minutes", 0),
        "alliedJungleMonsterKills": challenges.get("alliedJungleMonsterKills", 0),
        "baronTakedowns": challenges.get("baronTakedowns", 0),
        "blastConeOppositeOpponentCount": challenges.get("blastConeOppositeOpponentCount", 0),
        "bountyGold": challenges.get("bountyGold", 0),
        "buffsStolen": challenges.get("buffsStolen", 0),
        "completeSupportQuestInTime": challenges.get("completeSupportQuestInTime", 0),
        "controlWardsPlaced": challenges.get("controlWardsPlaced", 0),
        "damagePerMinute": challenges.get("damagePerMinute", 0),
        "damageTakenOnTeamPercentage": challenges.get("damageTakenOnTeamPercentage", 0),
        "dancedWithRiftHerald": challenges.get("dancedWithRiftHerald", 0),
        "deathsByEnemyChamps": challenges.get("deathsByEnemyChamps", 0),
        "dodgeSkillShotsSmallWindow": challenges.get("dodgeSkillShotsSmallWindow", 0),
        "doubleAces": challenges.get("doubleAces", 0),
        "dragonTakedowns": challenges.get("dragonTakedowns", 0),
        "earlyLaningPhaseGoldExpAdvantage": challenges.get("earlyLaningPhaseGoldExpAdvantage", 0),
        "effectiveHealAndShielding": challenges.get("effectiveHealAndShielding", 0),
        "enemyChampionImmobilizations": challenges.get("enemyChampionImmobilizations", 0),
        "enemyJungleMonsterKills": challenges.get("enemyJungleMonsterKills", 0),
        "epicMonsterKillsNearEnemyJungler": challenges.get("epicMonsterKillsNearEnemyJungler", 0),
        "epicMonsterKillsWithin30SecondsOfSpawn": challenges.get("epicMonsterKillsWithin30SecondsOfSpawn", 0),
        "epicMonsterSteals": challenges.get("epicMonsterSteals", 0),
        "epicMonsterStolenWithoutSmite": challenges.get("epicMonsterStolenWithoutSmite", 0),
        "firstTurretKilled": challenges.get("firstTurretKilled", 0),
        "flawlessAces": challenges.get("flawlessAces", 0),
        "fullTeamTakedown": challenges.get("fullTeamTakedown", 0),
        "gameLength": challenges.get("gameLength", 0),
        "goldPerMinute": challenges.get("goldPerMinute", 0),
        "hadOpenNexus": challenges.get("hadOpenNexus", 0),
        "highestCrowdControlScore": challenges.get("highestCrowdControlScore", 0),
        "immobilizeAndKillWithAlly": challenges.get("immobilizeAndKillWithAlly", 0),
        "initialBuffCount": challenges.get("initialBuffCount", 0),
        "initialCrabCount": challenges.get("initialCrabCount", 0),
        "jungleCsBefore10Minutes": challenges.get("jungleCsBefore10Minutes", 0),
        "junglerTakedownsNearDamagedEpicMonster": challenges.get("junglerTakedownsNearDamagedEpicMonster", 0),
        "kTurretsDestroyedBeforePlatesFall": challenges.get("kTurretsDestroyedBeforePlatesFall", 0),
        "kda": challenges.get("kda", 0),
        "killAfterHiddenWithAlly": challenges.get("killAfterHiddenWithAlly", 0),
        "killParticipation": challenges.get("killParticipation", 0),
        "killedChampTookFullTeamDamageSurvived": challenges.get("killedChampTookFullTeamDamageSurvived", 0),
        "killsNearEnemyTurret": challenges.get("killsNearEnemyTurret", 0),
        "killsOnOtherLanesEarlyJungleAsLaner": challenges.get("killsOnOtherLanesEarlyJungleAsLaner", 0),
        "killsOnRecentlyHealedByAramPack": challenges.get("killsOnRecentlyHealedByAramPack", 0),
        "killsUnderOwnTurret": challenges.get("killsUnderOwnTurret", 0),
        "killsWithHelpFromEpicMonster": challenges.get("killsWithHelpFromEpicMonster", 0),
        "knockEnemyIntoTeamAndKill": challenges.get("knockEnemyIntoTeamAndKill", 0),
        "landSkillShotsEarlyGame": challenges.get("landSkillShotsEarlyGame", 0),
        "laneMinionsFirst10Minutes": challenges.get("laneMinionsFirst10Minutes", 0),
        "laningPhaseGoldExpAdvantage": challenges.get("laningPhaseGoldExpAdvantage", 0),
        "legendaryCount": challenges.get("legendaryCount", 0),
        "lostAnInhibitor": challenges.get("lostAnInhibitor", 0),
        "maxCsAdvantageOnLaneOpponent": challenges.get("maxCsAdvantageOnLaneOpponent", 0),
        "maxKillDeficit": challenges.get("maxKillDeficit", 0),
        "maxLevelLeadLaneOpponent": challenges.get("maxLevelLeadLaneOpponent", 0),
        "mejaisFullStackInTime": challenges.get("mejaisFullStackInTime", 0),
        "moreEnemyJungleThanOpponent": challenges.get("moreEnemyJungleThanOpponent", 0),
        "multiKillOneSpell": challenges.get("multiKillOneSpell", 0),
        "multiTurretRiftHeraldCount": challenges.get("multiTurretRiftHeraldCount", 0),
        "multikills": challenges.get("multikills", 0),
        "outerTurretExecutesBefore10Minutes": challenges.get("outerTurretExecutesBefore10Minutes", 0),
        "outnumberedKills": challenges.get("outnumberedKills", 0),
        "outnumberedNexusKill": challenges.get("outnumberedNexusKill", 0),
        "perfectDragonSoulsTaken": challenges.get("perfectDragonSoulsTaken", 0),
        "perfectGame": challenges.get("perfectGame", 0),
        "pickKillWithAlly": challenges.get("pickKillWithAlly", 0),
        "playedChampSelectPosition": challenges.get("playedChampSelectPosition", 0),
        "quickFirstTurret": challenges.get("quickFirstTurret", 0),
        "quickSoloKills": challenges.get("quickSoloKills", 0),
        "riftHeraldTakedowns": challenges.get("riftHeraldTakedowns", 0),
        "saveAllyFromDeath": challenges.get("saveAllyFromDeath", 0),
        "scuttleCrabKills": challenges.get("scuttleCrabKills", 0),
        "skillshotsDodged": challenges.get("skillshotsDodged", 0),
        "skillshotsHit": challenges.get("skillshotsHit", 0),
        "snowballsHit": challenges.get("snowballsHit", 0),
        "soloKills": challenges.get("soloKills", 0),
        "stealthWardsPlaced": challenges.get("stealthWardsPlaced", 0),
        "survivedSingleDigitHpCount": challenges.get("survivedSingleDigitHpCount", 0),
        "survivedThreeImmobilizesInFight": challenges.get("survivedThreeImmobilizesInFight", 0),
        "takedownOnFirstTurret": challenges.get("takedownOnFirstTurret", 0),
        "takedowns": challenges.get("takedowns", 0),
        "takedownsAfterGainingLevelAdvantage": challenges.get("takedownsAfterGainingLevelAdvantage", 0),
        "takedownsBeforeJungleMinionSpawn": challenges.get("takedownsBeforeJungleMinionSpawn", 0),
        "takedownsFirstXMinutes": challenges.get("takedownsFirstXMinutes", 0),
        "takedownsInAlcove": challenges.get("takedownsInAlcove", 0),
        "takedownsInEnemyFountain": challenges.get("takedownsInEnemyFountain", 0),
        "teamBaronKills": challenges.get("teamBaronKills", 0),
        "teamDamagePercentage": challenges.get("teamDamagePercentage", 0),
        "teamElderDragonKills": challenges.get("teamElderDragonKills", 0),
        "teamRiftHeraldKills": challenges.get("teamRiftHeraldKills", 0),
        "tookLargeDamageSurvived": challenges.get("tookLargeDamageSurvived", 0),
        "turretPlatesTaken": challenges.get("turretPlatesTaken", 0),
        "turretsTakenWithRiftHerald": challenges.get("turretsTakenWithRiftHerald", 0),
        "twoWardsOneSweeperCount": challenges.get("twoWardsOneSweeperCount", 0),
        "visionScoreAdvantageLaneOpponent": challenges.get("visionScoreAdvantageLaneOpponent", 0),
        "visionScorePerMinute": challenges.get("visionScorePerMinute", 0),
        "voidMonsterKill": challenges.get("voidMonsterKill", 0),
        "wardTakedowns": challenges.get("wardTakedowns", 0),
        "wardTakedownsBefore20M": challenges.get("wardTakedownsBefore20M", 0),
        "wardsGuarded": challenges.get("wardsGuarded", 0),
    }


def batch_lookup(match: str, puuid: str, match_url: str):
    
    get_match_details_url = f"{match_url}/lol/match/v5/matches/{match}?api_key={league_api_key}"
    reponse_match_lookup = session.get(get_match_details_url)
    match_data = reponse_match_lookup.json()

    #logic to find where player is
    for i in range(10):
        participants_list = match_data["metadata"]["participants"]
        player_index = None

        if participants_list[i] == puuid:
            player_index = i;
            break;
    # Sometimes the data is malformed and thus somethings can be missed so this is to prevent whole code from crashing
    if player_index is None:
        print(f"⚠️ Skipping match {match} — puuid {puuid} not found among {len(participants_list)} participants")
        return None

    return extract_player_stats(player_index, match_data["info"]["participants"][player_index], match, puuid)


def get_whole_player_matchHistory(batch_size: int, puuid_stored: str, wait_time_batch: int, match_list: list, match_url: str):
    for i in range(0,len(match_list),batch_size):
        batch = match_list[i:i+batch_size]
        batch_insertion_matches = []
        for match in batch:
            match_data = batch_lookup(match, puuid_stored, match_url) ## returns a dict
            if match_data is not None:
                batch_insertion_matches.append(match_data)
        response = start_supabase.table("match_history").insert(batch_insertion_matches).execute()
        print(f"Inserted {len(batch_insertion_matches)} rows (batch {i // batch_size + 1}) ✅")
        if i + batch_size < len(match_list):
            print(f"Waiting {wait_time_batch}s before next batch...")
            time.sleep(wait_time_batch)

    print("Status == Player Match History ✅")



def main():
    #The vlaues will come from Frontend web
    gameName = input("What is your gameName: ")
    tagLine = input("What is your tagLine: ")
    print(PLATFORMS)
    platform = input("What is your region (na1, euw1, kr, etc.): ").lower()
    queue_type = input("What queue type (normal and ranked only)")

    ##Should also ahve a drop down in frontend later
    if (queue_type == "normal"):
        queue_id = 400

    if (queue_type == "ranked"):
        queue_id = 420
    # Change the values as needed
    batch_size = 20
    wait_time_batch = 25 # it should be 24-26 given the rate limit
    match_count = 100


    urls = get_urls(platform)
    base_url = urls["base_url"]
    match_url = urls["match_url"]

    ## Later in future we need to get this automated and we need a way to check if API key was expired

    puuid_stored = get_player_puuid(gameName,tagLine,match_url)

    if puuid_stored is None:
        print("❌ Could not find that player.")
        sys.exit(1)
    
    clear_puuid_specific_olddata(puuid_stored)
    # TRUNCATE TABLE champion_mastery, match_history RESTART IDENTITY; (Clear all data in tables in SQL Editor Supabase)

    #Mastery Table
    data_mastery = get_player_champions_mastery(puuid_stored, base_url)
    insert_only_played_mastery(puuid_stored, data_mastery)



    #Match History Table
    match_list = get_match_list(puuid_stored, match_count,queue_id, match_url)

    get_whole_player_matchHistory(batch_size,puuid_stored,wait_time_batch,match_list, match_url)

    print("Status == Completed Main✅")


if __name__ == "__main__":
    main()
