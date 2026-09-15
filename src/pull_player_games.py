import requests
import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime


###### REMMEMBER THIS IS  ONE PLAYER FUNCTIONALYIU NOT MORE THAN 1 CAN USE THIS AT ONCE OTHER BIG BANG WILL HAPPEN BOOM!

#loads env file
load_dotenv()

league_api_key = os.getenv("LEAGUE_API_KEY")

#The vlaues will come from Frontend web
# gameName = input("What is your gameName: ")
# tagLine = input("What is your tagLine: ")


#User will have dropdown to select region
base_url = f"https://na1.api.riotgames.com"


#SUPABASE DB stuff
db_url = os.environ["SUPABASE_URL"]
db_key = os.environ["SUPABASE_SECRET_KEY"]
start_supabase = create_client(db_url,db_key)

# PUUID STUFF
# get_puuid_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={league_api_key}"
# response_puuid = requests.get(get_puuid_url)
# response_dict_puuid = response_puuid.json()
# puuid_stored = response_dict_puuid["puuid"]
puuid_stored = "uFx-spv9qOYZQcGhPvtoHuNudgHSM6KUvVJlyvauO0H4pf-OpB8gT98uyJZqyYNPiTW5zlqdmxC_kw"


# #Delete Prev info and rewrite new one
# delete_table = (
#     start_supabase.table("champion_mastery")
#     .delete()
#     .eq("puuid",puuid_stored)
#     .execute()
# )






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
get_match_history_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid_stored}/ids?queue=400&start=0&count=100&api_key={league_api_key}"


def get_match_list():
    match_list_response = requests.get(get_match_history_url)
    return match_list_response.json()

def _i(value):
    """Safely convert a possibly-float Riot stat into a clean int for smallint/integer columns."""
    if value is None:
        return 0
    return int(round(value))


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

        # --- flattened from challenges, not nested ---
        "abilityUses": _i(challenges.get("abilityUses", 0)),
        "acesBefore15Minutes": _i(challenges.get("acesBefore15Minutes", 0)),
        "alliedJungleMonsterKills": _i(challenges.get("alliedJungleMonsterKills", 0)),
        "baronTakedowns": _i(challenges.get("baronTakedowns", 0)),
        "blastConeOppositeOpponentCount": _i(challenges.get("blastConeOppositeOpponentCount", 0)),
        "bountyGold": _i(challenges.get("bountyGold", 0)),
        "buffsStolen": _i(challenges.get("buffsStolen", 0)),
        "completeSupportQuestInTime": _i(challenges.get("completeSupportQuestInTime", 0)),
        "controlWardsPlaced": _i(challenges.get("controlWardsPlaced", 0)),
        "damagePerMinute": challenges.get("damagePerMinute", 0),
        "damageTakenOnTeamPercentage": challenges.get("damageTakenOnTeamPercentage", 0),
        "dancedWithRiftHerald": _i(challenges.get("dancedWithRiftHerald", 0)),
        "deathsByEnemyChamps": _i(challenges.get("deathsByEnemyChamps", 0)),
        "dodgeSkillShotsSmallWindow": _i(challenges.get("dodgeSkillShotsSmallWindow", 0)),
        "doubleAces": _i(challenges.get("doubleAces", 0)),
        "dragonTakedowns": _i(challenges.get("dragonTakedowns", 0)),
        "earlyLaningPhaseGoldExpAdvantage": challenges.get("earlyLaningPhaseGoldExpAdvantage", 0),
        "effectiveHealAndShielding": _i(challenges.get("effectiveHealAndShielding", 0)),
        "enemyChampionImmobilizations": _i(challenges.get("enemyChampionImmobilizations", 0)),
        "enemyJungleMonsterKills": _i(challenges.get("enemyJungleMonsterKills", 0)),
        "epicMonsterKillsNearEnemyJungler": _i(challenges.get("epicMonsterKillsNearEnemyJungler", 0)),
        "epicMonsterKillsWithin30SecondsOfSpawn": _i(challenges.get("epicMonsterKillsWithin30SecondsOfSpawn", 0)),
        "epicMonsterSteals": _i(challenges.get("epicMonsterSteals", 0)),
        "epicMonsterStolenWithoutSmite": _i(challenges.get("epicMonsterStolenWithoutSmite", 0)),
        "firstTurretKilled": _i(challenges.get("firstTurretKilled", 0)),
        "flawlessAces": _i(challenges.get("flawlessAces", 0)),
        "fullTeamTakedown": _i(challenges.get("fullTeamTakedown", 0)),
        "gameLength": challenges.get("gameLength", 0),
        "goldPerMinute": challenges.get("goldPerMinute", 0),
        "hadOpenNexus": _i(challenges.get("hadOpenNexus", 0)),
        "highestCrowdControlScore": _i(challenges.get("highestCrowdControlScore", 0)),
        "immobilizeAndKillWithAlly": _i(challenges.get("immobilizeAndKillWithAlly", 0)),
        "initialBuffCount": _i(challenges.get("initialBuffCount", 0)),
        "initialCrabCount": _i(challenges.get("initialCrabCount", 0)),
        "jungleCsBefore10Minutes": _i(challenges.get("jungleCsBefore10Minutes", 0)),
        "junglerTakedownsNearDamagedEpicMonster": _i(challenges.get("junglerTakedownsNearDamagedEpicMonster", 0)),
        "kTurretsDestroyedBeforePlatesFall": _i(challenges.get("kTurretsDestroyedBeforePlatesFall", 0)),
        "kda": challenges.get("kda", 0),
        "killAfterHiddenWithAlly": _i(challenges.get("killAfterHiddenWithAlly", 0)),
        "killParticipation": challenges.get("killParticipation", 0),
        "killedChampTookFullTeamDamageSurvived": _i(challenges.get("killedChampTookFullTeamDamageSurvived", 0)),
        "killsNearEnemyTurret": _i(challenges.get("killsNearEnemyTurret", 0)),
        "killsOnOtherLanesEarlyJungleAsLaner": _i(challenges.get("killsOnOtherLanesEarlyJungleAsLaner", 0)),
        "killsOnRecentlyHealedByAramPack": _i(challenges.get("killsOnRecentlyHealedByAramPack", 0)),
        "killsUnderOwnTurret": _i(challenges.get("killsUnderOwnTurret", 0)),
        "killsWithHelpFromEpicMonster": _i(challenges.get("killsWithHelpFromEpicMonster", 0)),
        "knockEnemyIntoTeamAndKill": _i(challenges.get("knockEnemyIntoTeamAndKill", 0)),
        "landSkillShotsEarlyGame": _i(challenges.get("landSkillShotsEarlyGame", 0)),
        "laneMinionsFirst10Minutes": _i(challenges.get("laneMinionsFirst10Minutes", 0)),
        "laningPhaseGoldExpAdvantage": challenges.get("laningPhaseGoldExpAdvantage", 0),
        "legendaryCount": _i(challenges.get("legendaryCount", 0)),
        "lostAnInhibitor": _i(challenges.get("lostAnInhibitor", 0)),
        "maxCsAdvantageOnLaneOpponent": challenges.get("maxCsAdvantageOnLaneOpponent", 0),
        "maxKillDeficit": _i(challenges.get("maxKillDeficit", 0)),
        "maxLevelLeadLaneOpponent": _i(challenges.get("maxLevelLeadLaneOpponent", 0)),
        "mejaisFullStackInTime": _i(challenges.get("mejaisFullStackInTime", 0)),
        "moreEnemyJungleThanOpponent": challenges.get("moreEnemyJungleThanOpponent", 0),
        "multiKillOneSpell": _i(challenges.get("multiKillOneSpell", 0)),
        "multiTurretRiftHeraldCount": _i(challenges.get("multiTurretRiftHeraldCount", 0)),
        "multikills": _i(challenges.get("multikills", 0)),
        "outerTurretExecutesBefore10Minutes": _i(challenges.get("outerTurretExecutesBefore10Minutes", 0)),
        "outnumberedKills": _i(challenges.get("outnumberedKills", 0)),
        "outnumberedNexusKill": _i(challenges.get("outnumberedNexusKill", 0)),
        "perfectDragonSoulsTaken": _i(challenges.get("perfectDragonSoulsTaken", 0)),
        "perfectGame": _i(challenges.get("perfectGame", 0)),
        "pickKillWithAlly": _i(challenges.get("pickKillWithAlly", 0)),
        "playedChampSelectPosition": _i(challenges.get("playedChampSelectPosition", 0)),
        "quickFirstTurret": _i(challenges.get("quickFirstTurret", 0)),
        "quickSoloKills": _i(challenges.get("quickSoloKills", 0)),
        "riftHeraldTakedowns": _i(challenges.get("riftHeraldTakedowns", 0)),
        "saveAllyFromDeath": _i(challenges.get("saveAllyFromDeath", 0)),
        "scuttleCrabKills": _i(challenges.get("scuttleCrabKills", 0)),
        "skillshotsDodged": _i(challenges.get("skillshotsDodged", 0)),
        "skillshotsHit": _i(challenges.get("skillshotsHit", 0)),
        "snowballsHit": _i(challenges.get("snowballsHit", 0)),
        "soloKills": _i(challenges.get("soloKills", 0)),
        "stealthWardsPlaced": _i(challenges.get("stealthWardsPlaced", 0)),
        "survivedSingleDigitHpCount": _i(challenges.get("survivedSingleDigitHpCount", 0)),
        "survivedThreeImmobilizesInFight": _i(challenges.get("survivedThreeImmobilizesInFight", 0)),
        "takedownOnFirstTurret": _i(challenges.get("takedownOnFirstTurret", 0)),
        "takedowns": _i(challenges.get("takedowns", 0)),
        "takedownsAfterGainingLevelAdvantage": _i(challenges.get("takedownsAfterGainingLevelAdvantage", 0)),
        "takedownsBeforeJungleMinionSpawn": _i(challenges.get("takedownsBeforeJungleMinionSpawn", 0)),
        "takedownsFirstXMinutes": _i(challenges.get("takedownsFirstXMinutes", 0)),
        "takedownsInAlcove": _i(challenges.get("takedownsInAlcove", 0)),
        "takedownsInEnemyFountain": _i(challenges.get("takedownsInEnemyFountain", 0)),
        "teamBaronKills": _i(challenges.get("teamBaronKills", 0)),
        "teamDamagePercentage": challenges.get("teamDamagePercentage", 0),
        "teamElderDragonKills": _i(challenges.get("teamElderDragonKills", 0)),
        "teamRiftHeraldKills": _i(challenges.get("teamRiftHeraldKills", 0)),
        "tookLargeDamageSurvived": _i(challenges.get("tookLargeDamageSurvived", 0)),
        "turretPlatesTaken": _i(challenges.get("turretPlatesTaken", 0)),
        "turretsTakenWithRiftHerald": _i(challenges.get("turretsTakenWithRiftHerald", 0)),
        "twoWardsOneSweeperCount": _i(challenges.get("twoWardsOneSweeperCount", 0)),
        "visionScoreAdvantageLaneOpponent": challenges.get("visionScoreAdvantageLaneOpponent", 0),
        "visionScorePerMinute": challenges.get("visionScorePerMinute", 0),
        "voidMonsterKill": _i(challenges.get("voidMonsterKill", 0)),
        "wardTakedowns": _i(challenges.get("wardTakedowns", 0)),
        "wardTakedownsBefore20M": _i(challenges.get("wardTakedownsBefore20M", 0)),
        "wardsGuarded": _i(challenges.get("wardsGuarded", 0)),
    }


def batch_lookup(match: str, puuid: str):
    
    get_match_details_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match}?api_key={league_api_key}"
    reponse_match_lookup = requests.get(get_match_details_url)
    match_data = reponse_match_lookup.json()

    #logic to find where player is
    for i in range(10):
        participants_list = match_data["metadata"]["participants"]
        player_index = None

        if participants_list[i] == puuid:
            player_index = i;
            break;
    if player_index is None:
        print(f"⚠️ Skipping match {match} — puuid {puuid} not found among {len(participants_list)} participants")
        return None

    return extract_player_stats(player_index, match_data["info"]["participants"][player_index], match, puuid)



batch_size = 20
wait_time_batch = 25
match_list = get_match_list()

for i in range(0,len(match_list),batch_size):
    batch = match_list[i:i+batch_size]
    batch_insertion_matches = []
    for match in batch:
        match_data = batch_lookup(match, puuid_stored) ## returns a dict
        if match_data is not None:
            batch_insertion_matches.append(match_data)
    response = start_supabase.table("match_history").insert(batch_insertion_matches).execute()
    print(f"Inserted {len(batch_insertion_matches)} rows (batch {i // batch_size + 1})")
    if i + batch_size < len(match_list):
        print(f"Waiting {wait_time_batch}s before next batch...")
        time.sleep(wait_time_batch)







# # #All the above will be functions you run inside a main or smthing

