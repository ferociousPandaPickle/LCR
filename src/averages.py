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


def extract_player_stats(player_index: int, participant: dict):
    challenges = participant.get("challenges", {})
    gold_earned = participant.get("goldEarned", 0)
    gold_spent = participant.get("goldSpent", 0)
    gold_spent_ratio = gold_spent / gold_earned if gold_earned > 0 else 0
    return {
        "championName": participant.get("championName"),
        "championId": participant.get("championId"),
        "teamPosition": participant.get("teamPosition"),
        "individualPosition": participant.get("individualPosition"),
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
        "goldEarned": gold_earned,
        "goldSpent": gold_spent,
        "goldSpentRatio": gold_spent_ratio,
        "goldPerMinute": challenges.get("goldPerMinute", 0),


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

