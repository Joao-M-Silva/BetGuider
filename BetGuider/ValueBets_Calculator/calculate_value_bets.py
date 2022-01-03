import unidecode
from fuzzywuzzy import process


def text_pp(x):
    """
    Post process of the text
    """
    x_pp = unidecode.unidecode(x)
    return x_pp.lower().strip()


def calculate_odds(df_hist, df_scrape):
    """
    Calculate GG and NG Odds 

    Parameters
    ----------
    df_hist : pd.DataFrame
        Historical Data 
    df_scape : pd.DataFrame
        Scraped Data

    Returns
    -------
    df_scraped

    """
    #All the Home Teams in the historical dataset
    hist_home_team_options = list(df_hist['Home Team'].unique())
    #All the Away Teams in the historical dataset
    hist_away_team_options = list(df_hist['Away Team'].unique())
    
    def teams_promoted_relegated(season:int):
        #Calculate the promoted or relegated teams for a given season
        #Teams promoted or relegated in season 20
        home_teams_promoted_relegated_season = list(df_hist.query('Home_Team_Promoted_Relegated == True and Season == @season')['Home Team'].unique())
        away_teams_promoted_relegated_season = list(df_hist.query('Away_Team_Promoted_Relegated == True and Season == @season')['Away Team'].unique())
        for team in away_teams_promoted_relegated_season:
            home_teams_promoted_relegated_season.append(team)
        teams_promoted_relegated_season = list(set(home_teams_promoted_relegated_season))
        return teams_promoted_relegated_season
        
    #Teams promoted or relegated in season 20
    teams_20_promoted_relegated = teams_promoted_relegated(20)
    #Teams promoted or relegated in season 21
    teams_21_promoted_relegated = teams_promoted_relegated(21)
    
    def real_odd(row, event:str='GG'):
        """
        Calculate the statistic probability of GG or NG

        """
        if event == 'GG':
            bts=True
        elif event == 'NG':
            bts=False
        #Scraped Home Team
        home_team = text_pp(row['Home Team'])
        #Scraped Away Team
        away_team = text_pp(row['Away Team'])
        #Matched Home Team
        match_home_team = process.extractOne(query=home_team, choices=hist_home_team_options)[0]
        #Matched Away Team
        match_away_team = process.extractOne(query=away_team, choices=hist_away_team_options)[0]
        if (match_home_team in teams_21_promoted_relegated) or (match_away_team in teams_21_promoted_relegated):
            return 0
        else:
            if (match_home_team in teams_20_promoted_relegated) or (match_away_team in teams_20_promoted_relegated):
                post_season = 19
            else:
                post_season = 18
            #Total Historical Games Home Team
            number_games_home_team = df_hist[df_hist['Home Team']==match_home_team].query('Season > @post_season').shape[0]
            #Total Historical Games Away Team
            number_games_away_team = df_hist[df_hist['Away Team']==match_away_team].query('Season > @post_season').shape[0]
            #Total Historical Games Home Team with BTS True
            bts_games_home_team = df_hist[df_hist['Home Team']==match_home_team].query('BTS == @bts and Season > @post_season').shape[0]
            #Total Historical Games Away Team with BTS True
            bts_games_away_team = df_hist[df_hist['Away Team']==match_away_team].query('BTS == @bts and Season > @post_season').shape[0]
            #BTS Probability
            prob = (bts_games_away_team+bts_games_home_team)/(number_games_away_team+number_games_home_team)
            return 1/prob
    
    #Calculate the probability of both teams scoring (BTS) for each scraped game
    df_scrape['Real_Odd_GG'] = df_scrape.apply(real_odd, event='GG', axis=1)
    df_scrape['Real_Odd_NG'] = df_scrape.apply(real_odd, event='NG', axis=1)
    
    #Calculate the difference between the Statistical and the Bookies Odds
    df_scrape['Diff_GG'] = df_scrape['Real_Odd_GG'] - df_scrape['Odd_GG']
    df_scrape['Diff_NG'] = df_scrape['Real_Odd_NG'] - df_scrape['Odd_NG']
    
    def avg_goals_per_season(row, home_away:str='Home', season:int=21):
        #Scraped Team
        team = text_pp(row[f'{home_away} Team'])
        #Matched Team
        if home_away == 'Home':
            match_team = process.extractOne(query=team, choices=hist_home_team_options)[0]
        elif home_away == 'Away':
            match_team = process.extractOne(query=team, choices=hist_away_team_options)[0]
        #Total Historical Games Season
        number_games = df_hist[df_hist[f'{home_away} Team']==match_team].query('Season == @season').shape[0]
        #Number of Goals Season
        number_goals = df_hist[df_hist[f'{home_away} Team']==match_team].query('Season == @season')[f'{home_away} Goals'].sum()
        #Average Goals Season
        avg_goals = number_goals / number_games
        return avg_goals
    
    #Calculate the average goals for the home and away teams regarding a specific season
    for home_away, season in zip(['Home', 'Home', 'Away', 'Away'], [20,21,20,21]):
        df_scrape[f'Avg_{home_away}_Goals_{season}'] = df_scrape.apply(avg_goals_per_season, home_away=home_away, season=season, axis=1)
    
    return df_scrape
    
                
def games_to_bet(df_scrape, event:str='GG', bank:int=1000, bet_p:float=0.01):
    """
    Get scrapped games to bet

    Parameters
    ----------
    df_scrape : pd.DataFrame
        Scraped data 
    event : str, optional
        Event type (The default is 'GG').
    bank : int, optional
        Total amount of money (The default is 1000).
    bet_p : float, optional
        Percentage of the bank to bet (The default is 0.01).

    Returns
    -------
    df_bet : pd.DataFrame
        Games to Bet

    """
    #Note -> only bet on probabilities higher than ~56 percent
    df_bet = df_scrape.query(f'Diff_{event} < 0 and Real_Odd_{event} < 1.8 and Real_Odd_{event} > 0') 
    
    #Expected Value
    def expected_value(x, bet:int, event:str):
        odd_bookie = x[f'Odd_{event}']
        odd = x[f'Real_Odd_{event}']
        p = 1 / odd
        income = bet*(odd_bookie-1)
        return income*p - bet*(1-p)
    
    #Function to calculate betting value
    def bet_value(x, event:str, order:str, bank:int, bet_p:float):
        p = 1/x[f'Real_Odd_{event}']
        base_amount = bank*bet_p
        if order == 'linear':
            v = base_amount*(2.22*p - 0.22)
            return v
        elif order == 'quadratic':
            v = base_amount*(1.858*p**2 + 0.438)
            return v
        elif order == 'uniform':
            v = base_amount
            return v
        
    #Apply Kelly Criterion for the betting value
    def bet_kelly_criterion(x, event:str, bank:int, f:float):
        p = 1/x[f'Real_Odd_{event}']
        odd_bookie = x[f'Odd_{event}']
        b = odd_bookie - 1
        fraction = (b*p-(1-p))/b
        return f*fraction*bank
        
    
    df_bet['Expected_Value'] = df_bet.apply(expected_value, bet=bank*bet_p, event=event, axis=1)
    df_bet['Bet_Uniform'] = df_bet.apply(bet_value, event=event, order='uniform', bank=bank, bet_p=bet_p, axis=1)
    df_bet['Bet_Linear'] = df_bet.apply(bet_value, event=event, order='linear', bank=bank, bet_p=bet_p, axis=1)
    df_bet['Bet_Quadratic'] = df_bet.apply(bet_value, event=event, order='quadratic', bank=bank, bet_p=bet_p, axis=1)
    df_bet['Bet_Kelly_Crit'] = df_bet.apply(bet_kelly_criterion, event=event, bank=bank, f=0.08, axis=1)
    df_bet['Gain_Uniform'] = df_bet.eval(f'Bet_Uniform*(Odd_{event})')
    df_bet['Gain_Linear'] = df_bet.eval(f'Bet_Linear*(Odd_{event})')
    df_bet['Gain_Quadratic'] = df_bet.eval(f'Bet_Quadratic*(Odd_{event})')
    df_bet['Gain_Kelly_Crit'] = df_bet.eval(f'Bet_Kelly_Crit*(Odd_{event})')
    df_bet['Income_Uniform'] = df_bet.eval(f'Bet_Uniform*(Odd_{event}-1)')
    df_bet['Income_Linear'] = df_bet.eval(f'Bet_Linear*(Odd_{event}-1)')
    df_bet['Income_Quadratic'] = df_bet.eval(f'Bet_Quadratic*(Odd_{event}-1)')
    df_bet['Income_Kelly_Crit'] = df_bet.eval(f'Bet_Kelly_Crit*(Odd_{event}-1)')
    
    return df_bet
    
    
    
        
    
    
    

