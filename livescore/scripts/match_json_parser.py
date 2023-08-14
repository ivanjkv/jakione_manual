import json
from datetime import datetime

TEAMS = [
	('ARS', 'Arsenal'),
	('AVA', 'Aston Villa'),
	('BRE', 'Brentford'),
	('BOU', 'Bournemouth'),
	('BRH', 'Brighton'),
	('BUR', 'Burnley'),
	('CFC', 'Chelsea'),
	('CRY', 'Crystal Palace'),
	('FUL', 'Fulham'),
	('EVE', 'Everton'),
	('LEE', 'Leeds'),
	('LEI', 'Leicester'),
	('LIV', 'Liverpool'),
    ('LUT', 'Luton'),
	('MCI', 'Manchester City'),
	('MUN', 'Manchester Utd'),
	('NEW', 'Newcastle'),
	('NTG', 'Nottingham'),
	('SOU', 'Southampton'),
    ('SHU', 'Sheffield Utd'),
	('TOT', 'Tottenham'),
	('WHU', 'West Ham'),
	('WLV', 'Wolves'),
	('WAT', 'Watford'),
]
MATCH_STATUS = [
        ('F', 'Finished'),
        ('L', 'Live'),
        ('S', 'Scheduled')
]

TEAMS_DICT = {key: value for value, key in TEAMS}
STATUS_DICT = {key: value for value, key in MATCH_STATUS}


dict_list = []
with open('livescore/data/2324/scrap_db.dat') as file:
    matches = file.readlines()
    for match in matches:
        match_list = match.strip('\n').split(', ')
        dict_entry = {
            'model': 'livescore.Match',
            'pk': match_list[0],
            'fields': {
                'match_time': datetime.strptime(match_list[1], '%d.%m.%Y %H:%M').strftime('%Y-%m-%d %H:%M'),
                'round': int(match_list[4]),
                'home_team': TEAMS_DICT[match_list[2]],
                'away_team': TEAMS_DICT[match_list[3]],
                'status': STATUS_DICT[match_list[5]],
                'home_goals': int(match_list[6]),
                'away_goals': int(match_list[7]),
                'minutes': 0
                }
            }
        dict_list.append(dict_entry)


with open('livescore/data/2324/matches.json', 'w') as file:
    file.write(json.dumps(dict_list))
