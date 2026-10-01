from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine
Base = declarative_base()

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key = True)
    api_id = Column(Integer, unique = True, nullable = False)
    name = Column(String, nullable = False)
    short_name = Column(String)

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key = True)
    api_id = Column(Integer, unique = True, nullable = False)
    season = Column(Integer)
    matchday = Column(Integer)
    stage = Column(String)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    home_goals = Column(Integer, nullable = True)
    away_goals = Column(Integer, nullable = True)
    status = Column(String)
    match_date = Column(DateTime)
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    
def get_engine():
    engine = create_engine("sqlite:///cl_predictor.db")

    return engine


if __name__ == "__main__":

    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Database created: cl_predictor.db")    



