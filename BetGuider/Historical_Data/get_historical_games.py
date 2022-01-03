import json
import unidecode
import pandas as pd
pd.set_option('display.max_columns', None)

def text_pp(x):
    """
    Post process of the text
    """
    x_pp = unidecode.unidecode(x)
    return x_pp.lower().strip()

def get_data_main_leagues(seasons:list, url:str="http://www.football-data.co.uk/mmz4281/",):
    """
    Function that obtains historical games for the main european football leagues

    Parameters
    ----------
    seasons : list
        Seasons of interest (ex.: seasons = [19,20,21]).
    url : str, optional
        Url of the source website (The default is "http://www.football-data.co.uk/mmz4281/")

    Returns
    -------
    df_hist : pd.DataFrame
        Dataframe containing the historical games 

    """
    #Dictionary with the main european leagues
    dict_countries = {
                  'Spanish La Liga':'SP1', 'Spanish Segunda Division':'SP2',
                  'German Bundesliga':'D1', 'German Bundesliga 2':'D2',
                  'Italian Serie A':'I1', 'Italian Serie B':'I2',
                  'English Premier League':'E0', 'English Championship':'E1', 'English League 1':'E2', 'English League 2':'E3',
                  'Scotish Premier League':'SC0', 'Scotish Division 1': 'SC1', 'Scotish Division 2':'SC2', 'Scotish Division 3':'SC3',
                  'French Ligue 1': 'F1', 'French Ligue 2':'F2',
                  'Dutch Eredivisie':'N1',
                  'Belgian First Division A':'B1',
                  'Portuguese Primeira Liga':'P1',
                  'Turkish Super League':'T1',
                  'Greek Super League':'G1',
                     }

    dict_historical_data = {} 
    #Create a dataframe of historical games for each league 
    for league in dict_countries:
        frames = []
        for season in seasons:
            try:
                df = pd.read_csv(url+str(season)+str(season+1)+"/"+dict_countries[league]+".csv")
            except: #Italian Serie B (0xa0 utf-8)
                df = pd.read_csv(url+str(season)+str(season+1)+"/"+dict_countries[league]+".csv", encoding='unicode_escape')
            df = df.assign(season=season)
            frames.append(df)
        df_frames = pd.concat(frames)
        dict_historical_data[league] = df_frames
        
    list_of_dfs = []
    #Concatenation of all the league dataframes containing historical games
    #into a single historical dataframe
    for league, df_league in dict_historical_data.items():
        list_of_dfs.append(df_league)
        
    df_hist = pd.concat(list_of_dfs)
    #Create a column for the League
    inv_map = {v: k for k, v in dict_countries.items()}
    df_hist['League'] = df_hist['Div'].apply(lambda x: inv_map[x])
    #Rename Columns
    df_hist = df_hist.rename(columns={"HomeTeam": "Home Team", 
                                      "AwayTeam": "Away Team",
                                      "FTHG":"Home Goals",
                                      "FTAG":"Away Goals",
                                      "HST":"Home Shots Target",
                                      "AST":"Away Shots Target",
                                      "HC":"Home Corners",
                                      "AC":"Away Corners",
                                      "season":"Season",
                                      "Time":"Hour",
                                      })
    

    df_hist = df_hist[['Div', 'League', 'Season', 'Date', 
                       'Hour', 'Home Team', 'Away Team', 
                       'Home Goals', 'Away Goals',
                       'Home Shots Target', 'Away Shots Target',
                       'Home Corners', 'Away Corners']]
    
    
             
    return df_hist


def df_extra_leagues_pp(df, seasons:list, seasons_info:dict, league:list, div:str,):
    """
    Function that rightly formats the Dataframe of the Extra Leagues
    
    Returns
    -------
    df : pd.DataFrame
        Formatted Dataframe

    """
    df['Season'] = df['Season'].replace(list(seasons_info.keys()), list(seasons_info.values()))
    #Filter the seasons to analyse
    df = df.query('Season in @seasons')
    #Filter the league to analyse
    df = df.query('League in @league')
    #Add a Div column
    df['Div'] = df.apply(lambda x: div, axis=1)
    #Rename Columns
    df = df.rename(columns={"Home": "Home Team", 
                            "Away": "Away Team",
                            "HG":"Home Goals",
                            "AG":"Away Goals",
                            "Time":"Hour",
                           })
    
    df = df[['Div', 'League', 'Season', 'Date', 'Hour', 'Home Team', 'Away Team', 'Home Goals', 'Away Goals']]
    
    return df
    

def get_data_extra_leagues(seasons:list, url:str="https://www.football-data.co.uk/new/",):
    with open('C:/Users/Asus/Documents/Python Scripts/BetGuider/Historical_Data/info_extra_leagues.json') as f:
        extra_leagues_info = json.load(f)
        
    dict_countries = {
                      'Argentina Primera Division':'ARG',
                      'Austria Bundesliga':'AUT',
                      'Brazil Serie A':'BRA',
                      'China Superleague':'CHN',
                      'Denmark Superliga':'DNK',
                      'Finland First League':'FIN',
                      'Ireland Premier Division':'IRL',
                      'Japan J-League':'JPN',
                      'Mexico Liga MX':'MEX',
                      'Norway Eliteserien':'NOR',
                      'Poland Ekstraklasa':'POL',
                      'Romania Liga 1':'ROU',
                      'Russia Premier League':'RUS',
                      'Sweden Allsvenskan':'SWE',
                      'Switzerland Super League':'SWZ',
                     }

    dict_new_historical_data = {}
    
    for league, div in dict_countries.items():
        df = pd.read_csv(url+div+'.csv')
        dict_new_historical_data[league] = df_extra_leagues_pp(df,
                                                               seasons=[19,20,21],
                                                               seasons_info=extra_leagues_info[div]['seasons'],
                                                               league=extra_leagues_info[div]['league'],
                                                               div=div)
      
    list_of_dfs = []
    for league, df_league in dict_new_historical_data.items():
        list_of_dfs.append(df_league)
    
    df_hist_extra = pd.concat(list_of_dfs)
    df_hist_extra['Season'] = df_hist_extra['Season'].astype('int64')
    return df_hist_extra


def get_historical_data(seasons:list=[19,29,21]):
    df_main_leagues = get_data_main_leagues(seasons=seasons)
    df_extra_leagues = get_data_extra_leagues(seasons=seasons)
    df_hist = pd.concat([df_main_leagues, df_extra_leagues])
    #Remove white space from the leagues
    df_hist['League'] = df_hist['League'].apply(lambda x: x.strip())
    
    #Add >2. goals column
    def more_2_goals(x):
        number_goals = x['Home Goals']+x['Away Goals']
        if number_goals > 2:
            return True
        elif number_goals <= 2:
            return False
        
    df_hist['More_2.5'] = df_hist.apply(more_2_goals, axis=1)
    
    #Add a BTS column
    def BTS(x):
        if x['Home Goals'] > 0 and x['Away Goals'] > 0:
            return True
        else:
            return False
        
    df_hist['BTS'] = df_hist.apply(BTS, axis=1)
    #Post process the home and away teams
    df_hist['Home Team'] = df_hist['Home Team'].apply(text_pp)
    df_hist['Away Team'] = df_hist['Away Team'].apply(text_pp)
    
    #Check promoted or relegated teams
    def teams_per_div(season:int, div:str):
        """
        Function that retrieves the teams per season and league

        Parameters
        ----------
        season : int
            Season of interest
        div : str
            Div (League) of interest

        Returns
        -------
        teams_season : list
            Teams of a league for a given season

        """
        home_teams_season = list(df_hist.query('Season == @season and Div == @div')['Home Team'].unique())
        away_teams_season = list(df_hist.query('Season == @season and Div == @div')['Away Team'].unique())
        
        for team in away_teams_season:
            home_teams_season.append(team)
        teams_season = list(set(home_teams_season))
        return teams_season
    
    def teams_per_season(season:int):
        """
        Create a Dictionary with the teams per league and per season

        Parameters
        ----------
        season : int
            Season of interest
        """
        return {div:teams_per_div(season, div) for div in df_hist['Div'].unique()}
    
    #Dictionary with the teams for each League for the seasons 19 and 20
    teams_per_season = {season:teams_per_season(season) for season in [19,20]}
    
    def team_promoted_relegated(x, home_away:str='Home'):
        """
        Function that returns True if a team was promoted or relegated in a given season

        Parameters
        ----------
        x : row
        
        home_away : str, optional
             The default is 'Home'.

        Returns
        -------
        bool
        """
        season = x['Season']
        team = x[f'{home_away} Team']
        div = x['Div']
        if season in [21,20]:
            if team not in teams_per_season[season-1][div]:
                return True
            else:
                return False
        else:
            return False
        
    df_hist['Home_Team_Promoted_Relegated'] = df_hist.apply(team_promoted_relegated, home_away='Home', axis=1)
    df_hist['Away_Team_Promoted_Relegated'] = df_hist.apply(team_promoted_relegated, home_away='Away', axis=1)
    #Convert Date to datetime
    df_hist['Date'] = pd.to_datetime(df_hist['Date'], format='%d/%m/%Y')
    
    def home_team_win(x):
        if x['Home Goals'] > x['Away Goals']:
            return True
        else:
            return False
    
    def draw(x):
        if x['Home Goals'] == x['Away Goals']:
            return True
        else:
            return False
    
    def away_team_win(x):
        if x['Home Goals'] < x['Away Goals']:
            return True
        else:
            return False
    
    df_hist['Home Team Win'] = df_hist.apply(home_team_win, axis=1)
    df_hist['Draw'] = df_hist.apply(draw, axis=1)
    df_hist['Away Team Win'] = df_hist.apply(away_team_win, axis=1)
        
    return df_hist


