from test_pull import get_cl_matches
#Reuses the function from test_pull.py and returns match data as a Dictonary
from models import Team, Match, get_engine
#Calls 2 database table classes and the function that connects to your SQLite file 
from sqlalchemy.orm import sessionmaker
# #The tool which lets you create a session for adding/querying/committing database changes
from datetime import datetime
#Used to convert the date strings into real pything datetime objects

engine = get_engine()

Session = sessionmaker(bind=engine)
session = Session()

#Creates a usable session and calls the API at run time and strores all responses

def get_or_create_team(session, team_data):

#Takes a session and a single teams raw dictionary, searches the teams table for a api_id which matches. Returns that row if found, else None
    existing = session.query(Team).filter_by(api_id = team_data["id"]).first()


    if existing is None:
        new_team = Team(api_id = team_data["id"], name = team_data["name"], short_name = team_data["shortName"])
        session.add(new_team)
        session.commit()
        
        return new_team

# if existing is None the team doesnt exist so builds a new Team object. Then staged and writted to the disk and returned

    else:
        return existing

#If the team already exists the row is returned


def get_or_create_match(session, match, home_team, away_team, season):

#Takes a session and a single matches raw dictionary, searches the matches table for a match with the same api_id

    existing = session.query(Match).filter_by(api_id = match["id"]).first()

    date_string = match["utcDate"]
    parsed = datetime.fromisoformat(date_string.replace("Z","+00:00"))

#Converts the API's date string into real python datetime objects

    if existing is None:
        new_match = Match(home_team = home_team, away_team = away_team, api_id = match["id"], season = season, matchday = match["matchday"], 
        stage = match["stage"], home_goals = match["score"]["fullTime"]['home'], away_goals = match["score"]["fullTime"]['away'] ,match_date = parsed, status = match["status"])
        session.add(new_match)
        session.commit()
        
        return new_match
    
#Passes the whole Team objects directly, rather than extracting their IDs as the relationship() fields handle that. if the match doesnt exist it will create a new one write it and return

    else:
        return existing

def sync_season(session, season):
    data = get_cl_matches(season = season)

#if the match already exists the row is returned

    for match in data["matches"]:
        home_team_data = match["homeTeam"]
        away_team_data = match["awayTeam"]
        home_team = get_or_create_team(session, home_team_data)
        away_team = get_or_create_team(session, away_team_data)

        new_match = get_or_create_match(session, match, home_team, away_team, season)

        print(home_team.name, new_match.home_goals, "-" , new_match.away_goals, away_team.name)

seasons = [2024,2025,2026]

for season in seasons:
    sync_season(session, season)

data = get_cl_matches(season=2026)

statuses = set()
for match in data["matches"]:
    statuses.add(match["status"])
print(statuses)