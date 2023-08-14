from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate

from django.db.models import Min, Max, Sum
from .models import Match, Prediction, User
from .forms import UploadFileForm

import zipfile, io, csv
import time


def livescores(request):
    '''
        This view returns live ranking
    '''
    # Find for live match
    start = time.perf_counter()
    live_games = Match.objects.filter(status__exact='L')

    # Get users
    users = Prediction.objects.values('user').order_by('user').annotate(points = Sum('points')).order_by('-points')
    live_points = [0]*len(users)

    for i, user in enumerate(users):
        # Filter live users predictions
        live_matches = Prediction.objects.filter(user__userid__exact=user['user']).filter(match__status__exact='L')
        # Determine the sum of points (live) for each rank
        live_points[i] = sum([match.live_points for match in live_matches])
        
    # Sort all users by points (descending)
    live_sorted = sorted(range(len(live_points)), key=lambda i: users[i]['points']+live_points[i], reverse=True)
    ranking_data = [{
        'user': User.objects.get(pk=users[past_rank]['user']),
        'points': users[past_rank]['points']+live_points[past_rank],
        'change': live_rank-past_rank,
        'points_live': live_points[past_rank]
        } for live_rank, past_rank in enumerate(live_sorted)]

    return render(request, 'livescore/livescores.html', {
        'page_title': 'Livescores',
        'live_games': live_games,
        'rankings': ranking_data,
        'render_time': f'{(time.perf_counter()-start)*1000:.0f} ms'
    })

def fixtures(request):
    '''
        This view lists all Match(es) split (filteres) by the round (GameWeek)
    '''
    # Initialize matches dictionary {round: match QuerySet}
    matches = {}
    last_gw = 0
    # Filter matches for the given round.
    for i in range(1, 39):
        matches[i] = Match.objects.filter(round__exact=i).order_by('match_time')
        # If all fixtures are finished, GW is finished
        if len(matches[i].filter(match_time__lte=timezone.now()+timezone.timedelta(hours=2)))==10:
            last_gw = i

    return render(request, 'livescore/fixtures.html', {
        'page_title': 'Fixtures',
        'matches': matches,
        'current_gw': last_gw+1
    })

def user(request, userid=''):
    '''
        This view lists all Prediction(s) for the given User.
    '''
    user = User.objects.get(pk=userid)
    max_round = Prediction.objects.aggregate(Max('match__round'))['match__round__max']
    predictions = [Prediction.objects.filter(user__exact=userid).filter(match__round__exact=i+1).exclude(match__status__exact='P') for i in range(max_round)]
    total = Prediction.objects.filter(user__exact=userid).aggregate(Sum('points'))['points__sum']

    return render(request, 'livescore/user.html', {
        'page_title': f'User {user}',
        'user': user,
        'total': total,
        'predictions': predictions
    })

def match(request, matchid=''):
    '''
        This view lists all Prediction(s) for the given Match and provides a basic data if the fixture is ongoing.
    '''
    match = Match.objects.get(pk=matchid)
    predictions = Prediction.objects.filter(match__exact=matchid)
    
    return render(request, 'livescore/match.html', {
        'page_title': f'Match {match}',
        'match': match,
        'predictions': predictions
    })

def privacy(request):
    '''
        Mandatory privacy policy.
    '''
    return render(request, 'livescore/privacy.html', {
        'page_title': 'About | Privacy policy',
    })

def deadlines(request):
    '''
        This view lists all deadlines by filtering Match(es) table by round (GameWeek)
    '''
    # Initialize deadlines dictionary {round: [match_time, has_passed]}
    deadlines = {}
    # Filter matches for the given round (GW), find the earliest time/date ('match_time__min')
    for i in range(38):
        deadlines[i+1] = [  Match.objects.filter(round__exact=i+1).aggregate(Min('match_time'))['match_time__min'],
                            Match.objects.filter(round__exact=i+1).aggregate(Min('match_time'))['match_time__min']<timezone.now()]
    return render(request, 'livescore/deadlines.html', {
        'page_title': 'Deadlines',
        'deadlines': deadlines,
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('livescores')
        else:
            messages.success(request, 'Wrong username or password!')
            return redirect('login')
        
    else:
        return render(request, 'livescore/login.html', {})
    
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out.')
    return redirect('livescores')

def update_scores(request):
    if request.method == "POST":
        round = int(request.POST['round'])
        matches = Match.objects.filter(round__exact=round).order_by('match_time')

        if 'Save' in request.POST:
            round = int(request.POST['round'])
            matches = Match.objects.filter(round__exact=round).order_by('match_time')
            for match in Match.objects.filter(round__exact=round):
                match.home_goals = int(request.POST[f'home_{match.pk}'])
                match.away_goals = int(request.POST[f'away_{match.pk}'])
                match.status = request.POST[f'status_{match.pk}']
                match.save()
            messages.success(request, 'Changes saved.')
            
        return render(request, 'livescore/update_scores.html', {'select_round': False,
                                                                'round': round,
                                                                'range': range(1, 39),
                                                                'matches': matches})
    else:
        return render(request, 'livescore/update_scores.html', {'select_round': True,
                                                                'range': range(1, 39)})

def upload_predictions(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            # Handle zipped .csv file
            zip_file = zipfile.ZipFile(uploaded_file.file)
            with zip_file.open(zip_file.namelist()[0], 'r') as bytesCSV:
                filedata = list(csv.reader(io.TextIOWrapper(bytesCSV, 'utf-8'),delimiter=';'))
                # extract games
                header_row = filedata[0][2:]
                fixtures = [fixture.split(' - ') for fixture in header_row]
                for row in filedata[1:]:
                    userid = row[1]
                    for index, prediction in enumerate(row[2:]):
                        if prediction!='' and prediction!='-:-':
                            HG, AG = prediction.split(':')
                            obj, created = Prediction.objects.get_or_create(
                                user=User.objects.filter(userid__exact=userid)[0],
                                match=Match.objects.filter(home_team__exact=fixtures[index][0]).filter(away_team__exact=fixtures[index][1])[0],
                                home_goals=HG,
                                away_goals=AG,
                            )
        return redirect('livescores')
    else:
        form = UploadFileForm()
        return render(request, 'livescore/upload_predictions.html', {'form': form})