import json
import pandas as pd
from pathlib import Path

DATA_DIR = Path(".")  # ensure roster.json is here


roster_path = DATA_DIR / "roster.json"
with roster_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

data.keys(), list(data.keys())


players_df_3 = pd.DataFrame([
    {
        "player_id": p.get("id"),
        "player_name": p.get("name"),
        "jersey": p.get("jersey"),
        "first_name": p.get("first_name"),
        "last_name": p.get("last_name"),
        "name_suffix": p.get("name_suffix"),     # Optional
        "abbr_name": p.get("abbr_name"),
        "weight": p.get("weight"),
        "height": p.get("height"),
        "position": p.get("position"),
        "birth_place": p.get("birth_place"),
        "birth_date": p.get("birth_date"),       # Optional
        "status": p.get("status"),
        "eligibility": p.get("eligibility"),
        "team_id": data["id"],
    }
    for p in data.get("players", [])
])

team_df = pd.DataFrame([{
    "team_id": data.get("id"),
    "team_name": data.get("name"),
    "market": data.get("market"),
    "alias": data.get("alias"),
    "founded": data.get("founded"),
    "mascot": data.get("mascot"),
    "fight_song": data.get("fight_song"),
    "championships_won": data.get("championships_won"),
    "conference_titles": data.get("conference_titles"),
    "playoff_appearances": data.get("playoff_appearances"),

    # foreign key references
    "venue_id": data.get("venue", {}).get("id"),
    "division_id": data.get("division", {}).get("id"),
    "conference_id": data.get("conference", {}).get("id"),
    "franchise_id": data.get("franchise", {}).get("id"),
}])

venue = data.get("venue", {})

venue_df = pd.DataFrame([{
    "venue_id": venue.get("id"),
    "venue_name": venue.get("name"),
    "city": venue.get("city"),
    "state": venue.get("state"),
    "country": venue.get("country"),
    "zip": venue.get("zip"),
    "address": venue.get("address"),
    "capacity": venue.get("capacity"),
    "surface": venue.get("surface"),
    "roof_type": venue.get("roof_type"),
    "sr_id": venue.get("sr_id"),
    "lat": venue.get("location", {}).get("lat"),
    "lng": venue.get("location", {}).get("lng"),
}])

division = data.get("division", {})

division_df = pd.DataFrame([{
    "division_id": division.get("id"),
    "division_name": division.get("name"),
    "division_alias": division.get("alias"),
}])


conference = data.get("conference", {})

conference_df = pd.DataFrame([{
    "conference_id": conference.get("id"),
    "conference_name": conference.get("name"),
    "conference_alias": conference.get("alias"),
}])


franchise = data.get("franchise", {})

franchise_df = pd.DataFrame([{
    "franchise_id": franchise.get("id"),
    "franchise_name": franchise.get("name"),
}])


coaches_df = pd.DataFrame([
    {
        "coach_id": c.get("id"),
        "full_name": c.get("full_name"),
        "first_name": c.get("first_name"),
        "last_name": c.get("last_name"),
        "position": c.get("position"),
        "team_id": data.get("id")  # FK
    }
    for c in data.get("coaches", [])
])


players_df_3
team_df
venue_df
division_df
conference_df
franchise_df
coaches_df