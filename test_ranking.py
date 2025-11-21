import requests
import pandas as pd
import json # convert to python object


# Extract Data from API
url = "https://api.sportradar.com/ncaafb/trial/v7/en/polls/AP25/2025/01/rankings.json"

headers = {
    "accept": "application/json",
    "x-api-key": "n2TZzOYtgSSCFivhd5XuJBDabmRWPZC45zwo8Z5T"
}

response = requests.get(url, headers=headers)

# print(response.text)

## Convert JSON response to Python object

data = json.loads(response.text)
data


print(json.dumps(data, indent=4))

# Create DataFrame
poll_info={
'poll_id"': data['poll']['id'],
'poll_alias:': data['poll']['alias'],
'poll_name': data['poll']['name'],
'season': data['season'],
'week': data['week'],
'effective_time': data['effective_time']
}
poll_df = pd.DataFrame([poll_info])
print(poll_df)



rankingdata = data
rows = []

for team in rankingdata.get("rankings", []):
    rows.append({
        "poll_id": rankingdata["poll"].get("id"),
        "poll_name": rankingdata["poll"].get("name"),
        "poll_alias": rankingdata["poll"].get("alias"),
        "season": rankingdata.get("season"),
        "week": rankingdata.get("week"),
        "effective_time": rankingdata.get("effective_time"),

        "team_id": team.get("id"),
        "team_name": team.get("name"),
        "team_market": team.get("market"),
        "rank": team.get("rank"),
        "points": team.get("points"),
        "first_place_votes": team.get("fp_votes")
    })

df_rankings = pd.DataFrame(rows)
print(df_rankings)