from django.db import models
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver

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
MATCH_OUTCOME = [
    ('1', '1'),
    ('2', '2'),
    ('X', 'X')
]

class User(models.Model):
    userid = models.CharField('User ID', primary_key=True, max_length=8, unique=True)
    name = models.CharField('Name', max_length=30)
    email = models.EmailField('E-mail')

    def __str__(self):
        return self.name

class Match(models.Model):
    MATCH_STATUS = [
        ('F', 'Finished'),
        ('L', 'Live'),
        ('S', 'Scheduled'),
        ('P', 'Postponed')
    ]
    matchid = models.CharField('Match ID', primary_key=True, max_length=8, unique=True)
    match_time = models.DateTimeField('Time')
    round = models.IntegerField('Round', default=1)
    home_team = models.CharField('Home Team', max_length=30, choices=TEAMS, default='ARS')
    away_team = models.CharField('Away Team', max_length=30, choices=TEAMS, default='AVA')
    status  = models.CharField('Status', max_length=10, choices=MATCH_STATUS, default='S')
    previous_status = models.CharField('Prev. Status', max_length=10, choices=MATCH_STATUS, default='S')
    home_goals = models.IntegerField('Home Goals', default=0)
    away_goals = models.IntegerField('Away Goals', default=0)
    minutes = models.IntegerField('Minutes', default=0)

    @property
    def outcome(self):
        HG = self.home_goals
        AG = self.away_goals
        # Formula to convert [-1,0,1] outcomes to [1,X,2]
        return str(int(0.5*((int(AG)-int(HG))/abs(int(AG)-int(HG))+3))) if AG!=HG else 'X'

    def __str__(self):
        return self.home_team + '-' + self.away_team

@receiver(post_init, sender=Match)
def set_previous_status(sender, instance, **kwargs):
    instance.previous_status = instance.status

@receiver(post_save, sender=Match)
def change_status(sender, instance, created, **kwargs):
    if not created:
        is_status_changed = instance.previous_status != instance.status
        if is_status_changed:
            affected_predictions = Prediction.objects.filter(match__exact=instance)
            for prediction in affected_predictions:
                if instance.status == 'F':
                    prediction.points = prediction.live_points
                prediction.save()

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_goals = models.IntegerField('Home Goals')
    away_goals = models.IntegerField('Away Goals')
    points = models.IntegerField('Points', default=0)

    @property
    def outcome(self):
        HG = self.home_goals
        AG = self.away_goals
        # Formula to convert [-1,0,1] outcomes to [1,X,2]
        return str(int(0.5*((int(AG)-int(HG))/abs(int(AG)-int(HG))+3))) if AG!=HG else 'X'

    @property
    def live_points(self):
            match = Match.objects.get(pk=self.match.matchid)
            HG = match.home_goals
            AG = match.away_goals
            outcome = match.outcome
            points = 0
            if match.status!='S':
            # Point calculation
                if outcome == self.outcome:
                    points += 2
                if HG==self.home_goals:
                    points += 1
                if AG==self.away_goals:
                    points += 1
                if (HG-AG)==(self.home_goals-self.away_goals):
                    points += 1
            return points

    def __str__(self):
        return f'{self.user.name}:{self.match.home_team}-{self.match.away_team}'
