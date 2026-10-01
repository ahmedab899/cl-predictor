"""
Throwaway test script — Week 1, Step 1.

Purpose: confirm we can load the API key from .env and pull real
Champions League match data using Python + requests, instead of curl.

This file is NOT part of the real app. It's just a sanity check.
"""

import os
from dotenv import load_dotenv
import requests

# Load variables from .env into the environment
load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

if not API_KEY:
    raise ValueError(
        "No API key found. Check that .env exists and contains "
        "FOOTBALL_DATA_API_KEY=your_key_here"
    )

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}


def get_cl_matches(season: int):
    """Fetch all Champions League matches for a given season year."""
    url = f"{BASE_URL}/competitions/CL/matches"
    params = {"season": season}

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()  # raises an error if the request failed

    return response.json()


if __name__ == "__main__":
    data = get_cl_matches(season=2024)

    matches = data["matches"]
    print(f"Pulled {len(matches)} matches for the 2024/25 season.\n")

    # Print the first 5 matches as a sanity check
    for match in matches[:5]:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        home_goals = match["score"]["fullTime"]["home"]
        away_goals = match["score"]["fullTime"]["away"]
        date = match["utcDate"][:10]

        print(f"{date}: {home} {home_goals} - {away_goals} {away}")
