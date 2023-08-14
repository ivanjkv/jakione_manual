import requests
import re
from bs4 import BeautifulSoup
from time import sleep

matchlist = []
i=0
with open('livescore/data/2324/id.dat') as f:
    for line in f.readlines():
        try:
            matchid = line.strip()
            # WEBSITE URL
            url = f'https://www.flashscore.com/match/{matchid}/#/match-summary'
            r = requests.get(url)
            
            # SOUP-IT!
            soup = BeautifulSoup(r.text, 'lxml')
            
            #name = soup.find("meta", attrs={'name':'og:title'})
            #home_team, away_team = re.findall(r'([\w+\s]+)\s-\s([\w+\s]+)\d*:*\d*',name['content'])[0]
            
            # ROUND NUMBER (cannot scrap from the mobile version)
            desc = soup.find("meta", attrs={'name':'og:description'})
            rnd = str(re.findall(r'[\w+\s]+-\sRound\s(\d+)', desc['content'])[0])
            
            # MOBILE URL
            urlm = f'http://www.flashscore.mobi/match/{matchid}/'
            r = requests.get(urlm)
            
            # SOUP-IT!
            soup = BeautifulSoup(r.text, 'xml')
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
                
            # Formula to convert [-1,0,1] outcomes to [1,X,2]
            outcome = str(int(0.5*((int(AG)-int(HG))/abs(int(AG)-int(HG))+3))) if AG!=HG else 'X'
            matchlist.append([matchid, date, home_team, away_team, rnd, status, HG, AG, outcome])
            print(f'{i}, ',end='')
            i+=1
            sleep(0.5)
        except:
            print(line)
with open('livescore/data/2324/scrap_db.dat', 'w') as f:
    for match in matchlist:
        f.write(', '.join(match)+'\n')
