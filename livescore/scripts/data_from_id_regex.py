import requests
import re
from bs4 import BeautifulSoup
from time import sleep

def scrape(matchid='bLacZ716'):

    # MOBILE URL
    urlm = f'http://www.flashscore.mobi/match/{matchid}/'
    r = requests.get(urlm)

    # SOUP-IT!
    soup = BeautifulSoup(r.text, 'html.parser')
    home_team, away_team = soup.find("h3").get_text().split(' - ')
    
    divs = soup.find_all("div", attrs={'class':'detail'})
    # Determine game status from the number of <div> tags
    if len(divs) >= 3:
        # Game in play or finished
        if divs[1].get_text()=='Finished':
            HG, AG = (divs[0].get_text().split()[0]).split(':')
            status = 'Finished'
            date = divs[2].get_text()
        else:
            HG, AG = (divs[0].get_text().split()[0]).split(':')
            minutes = (divs[1].get_text().split('-')[1].strip('+\''))
            status = 'Live'
            date = divs[2].get_text()            
    else:
        # Game scheduled or postponed
        HG, AG = '0', '0'
        status = 'Scheduled'
        date = divs[-1].contents[0]

    return [matchid, date, home_team, away_team, status, HG, AG]

print(scrape())