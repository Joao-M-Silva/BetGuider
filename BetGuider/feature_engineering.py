import pandas as pd
from datetime import date, timedelta


def league_average_goals(x, df, home_away:str, seasons:list):
    """
    Average goals per league

    Parameters
    ----------
    x : 
        row of the historical data dataframe.
    df : pd.DataFrame
        historical data dataframe.
    home_away : str
        reference to calculations
        Options: Home, Away.
    seasons : list
        seasons of interest.
    """
    if home_away not in ['Home', 'Away']:
        raise Exception('Bad home_away argument. Options are Home and Away')
        
    #League
    div = x['Div']
    #Date
    game_date = x['Date']
    #Only consider games that happened before and including
    #the prior week
    limit_date = game_date - timedelta(weeks=1)
    df = df.query('(Date<=@limit_date) and (Season in @seasons) and (Div==@div)')
    total_goals = df[f'{home_away} Goals'].sum()
    total_matchs = df.shape[0]
    avg_goals = total_goals / total_matchs
    
    return avg_goals
    

def team_average_goals(x, df, home_away:str, seasons:list, 
                       sample:int=None, scored_conceded:str='scored'):
    """
    Average Goals Scored or Conceded per Team

    Parameters
    ----------
    x : 
        row of the historical data dataframe.
    df : pd.DataFrame
        historical data dataframe.
    home_away : str
        reference to calculations
        Options: Home, Away.
    seasons : list
        seasons of interest.
    sample : int, optional
        Number of games to include in the calculations. 
        The default is None.
    scored_conceded:str, optional
        indicator to calculate average goals scored or conceded
        The default is scored.
        Options:
            scored, conceded
    """
    if home_away not in ['Home', 'Away']:
        raise Exception('Bad home_away argument. Options are Home and Away.')
    
    if scored_conceded not in ['scored', 'conceded']:
        raise Exception('Bad scored_conceded argument. options are scored and conceded.')
    
    game_date = x['Date']
    limit_date = game_date - timedelta(weeks=1)
    team = x[f'{home_away} Team']
    query = f'(Date<=@limit_date) and (Season in @seasons) and (`{home_away} Team`==@team)'
    query = query.replace('\n','')
    df = df.query(query)

    if sample:
        df = df.sort_values('Date', ascending=False).head(sample)
     
    if scored_conceded == 'scored':
        conv_ = {'Home':'Home',
                 'Away':'Away',}
    elif scored_conceded == 'conceded':
        conv_ = {'Home':'Away',
                 'Away':'Home',}
    
    home_away = conv_[home_away]
    total_goals = df[f'{home_away} Goals'].sum()
    total_matchs = df.shape[0]
    avg_goals = total_goals / total_matchs
    
    return avg_goals
        
    
                  
                 