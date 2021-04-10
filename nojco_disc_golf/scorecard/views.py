from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.http import JsonResponse
from django.core import serializers
import pprint

from .models import Round, Player, Hole, Course, Score


class IndexView(generic.ListView):
    model = Course
    template_name = 'scorecard/index.html'

    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['courses'] = Course.objects.all()
        context['rounds'] = Round.objects.filter(active=True)
        return context

class PreviousRounds(generic.ListView):
    model = Round
    template_name = 'scorecard/previous_rounds.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['courses'] = Course.objects.all()
        context['rounds'] = Round.objects.filter(active=False).order_by('-date')
        return context
    


class RoundView(generic.DetailView):
    model = Round
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['players'] = Player.objects.all()
        context['score_options'] = range(10)
        context['autosave'] = True
        holes = self.object.hole_set.all()
        # print (holes)

        return context

class HoleView(generic.DetailView):
    model = Hole


# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = 'polls/results.html'

# /scorecard/new_round?course=<id>
def new_round(request):
    # Get the requested course
    try:
        course = Course.objects.get(pk=request.POST['course'])
    except (KeyError, Course.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'scorecard/error.html', {
            'course': request.POST['course'],
            'error_message': "You didn't select a valid course.",
        })
    else:
        # Set the title based on the posted info or pull from the course
        try:
            if (not request.POST['title']):
                rt = course.name
            else:
                rt=request.POST['title']
        except:
            rt = course.name
        
        # Create a round from the course
        rnd = course.round_set.create( title = rt, date = timezone.now())

        # Create holes for the round
        if (course.holes > course.coursehole_set.count()):

            for i in range(course.holes) :
                rnd.hole_set.create(hole_num = i+1)
        else:
            for ch in course.coursehole_set.all():
                rnd.hole_set.create(hole_num = ch.hole_num, par = ch.par, distance = ch.distance)
                
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        # Send user to the round view to add players/track scores
        return HttpResponseRedirect(reverse('scorecard:round', args=(rnd.id,)))

# /scorecard/add_player_to_round/<round>
def add_player_to_round(request, roundid, playerid):
    # Get the requested course
    try:
        rnd = Round.objects.get(pk=roundid)
    except (KeyError, Round.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'scorecard/error.html', {
            'round': roundid,
            'error_message': "You didn't select a valid round.",
        })
    # Get the requested Player
    try:
        player = Player.objects.get(pk=playerid)
    except (KeyError, Player.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'scorecard/error.html', {
            'round': roundid,
            'player': playerid,
            'error_message': "You didn't select a valid player.",
        })

    rnd.roundplayers_set.get_or_create(player=player, handicap=round(player.handicap * (rnd.hole_set.count() / 18)))
    
    # Create holes for the round
    # TBD: Should allow tempalte holes tied to course to set par
    for hole in rnd.hole_set.all() :
        player.score_set.get_or_create(hole=hole, round=rnd)
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    # Send user to the round view to add players/track scores
    return HttpResponseRedirect(reverse('scorecard:round', args=(rnd.id,)))

# /scorecard/save_scores/<round>
def save_scores(request, roundid):
    # Get the requested round
    try:
        round = Round.objects.get(pk=roundid)
    except (KeyError, Round.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'scorecard/error.html', {
            'round': roundid,
            'error_message': "You didn't select a valid round.",
        })
    #print (request.POST)
   # print (request.GET)
    for key, value in request.POST.items() :
        scoreid = key.split("-", 1)[1]
        score = Score.objects.get(pk=scoreid)
        score.score = value
        score.save()


    response = {
        'success' : True
    }

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    # Send user to the round view to add players/track scores
    return JsonResponse(response)

# /scorecard/complete_round/<round>
def complete_round(request, roundid):
    # Get the requested round
    try:
        round = Round.objects.get(pk=roundid)
    except (KeyError, Round.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'scorecard/error.html', {
            'round': roundid,
            'error_message': "You didn't select a valid round.",
        })
    round.active=False
    round.save()
    return HttpResponseRedirect(reverse('scorecard:index'))

# /scorecard/delete_round/<round>
def delete_round(request, roundid):
    # Get the requested round
    try:
        round = Round.objects.get(pk=roundid)
    except (KeyError, Round.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'scorecard/error.html', {
            'round': roundid,
            'error_message': "You didn't select a valid round.",
        })
    round.delete()
    return HttpResponseRedirect(reverse('scorecard:index'))

# /scorecard/current_round
def current_round(request):
    # Get the requested round
    try:
        round = Round.objects.filter(active=True).latest('date')
    except (KeyError, Round.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'scorecard/error.html', {
            'error_message': "No current round found.",
        })

    return HttpResponseRedirect(reverse('scorecard:round', args=(round.id,)))

class PlayerHandicaps(generic.ListView):
    model = Player
    template_name = 'scorecard/player_handicaps.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['players'] = Player.objects.all().order_by('handicap')
        context['rounds'] = Round.objects.all()
        return context

# /scorecard/delete_round/<round>
def calculate_handicaps(request):
    # Loop over all players
    for player in Player.objects.all():
        # Get last 3 complete rounds
        roundplayers = player.roundplayers_set.order_by("-round__date")[:5]
        # for each round
        round_total = 0
        rounds = 0
        best_round = {
            'delta' : 100
        } 
        for roundplayer in roundplayers:
            # for each score
            total = 0
            holes = 0
            for score in Score.objects.filter(round = roundplayer.round, player = player):
                # total score (raw) 
                # TODO: add per hole par
                total += score.score
                holes += 1
            if holes == 0:
                continue
            # Subtract par for course to get relative difference
            delta1 = total - roundplayer.round.course.par
            delta = delta1 /  (holes / 18)
            #print ("%s - %s - %s - %s - %s" % (player.name, roundplayer.round.title, delta1, delta , holes))
            # Combine total-par
            round_total += delta
            rounds += 1
            if delta1 < best_round['delta']:
                best_round['delta'] = delta1
                best_round['round'] = roundplayer.round.pk
        # Average over 3 rounds, with a factor
        #print (rounds)
        if rounds > 0:
            hdcp = (round_total/rounds) * .75
            # If changed, create historical
            if (True or round(hdcp) != player.handicap):
                
                #print ("%s - %s -> %s" % (player.name, player.handicap , hdcp))
                player.historicalhandicaps_set.create(handicap = hdcp, handicap_date = player.handicap_date)
                # Update player and save
                player.handicap = round(hdcp)
                player.handicap_date = timezone.now()
                player.best_round_id = best_round['round']
                player.best_delta = best_round['delta']
                player.rounds_counted = rounds
                player.save()

    
    return HttpResponseRedirect(reverse('scorecard:player_handicaps'))

    
def new_player(request):
    player_name = request.POST['name']
    player, created = Player.objects.get_or_create(name=player_name)
    player.save()
    return player.pk


# /scorecard/add_new_player_to_round/<round>
def add_new_player_to_round(request, roundid):
    playerid = new_player(request)
    return add_player_to_round(request, roundid, playerid)
    
# /scorecard/update_scores/<round>
def update_scores(request, roundid):
    # Get the requested round
    try:
        rnd = Round.objects.get(pk=roundid)
    except (KeyError, Round.DoesNotExist):
        # Redisplay the question voting form.
        return JsonResponse ({
            'round': roundid,
            'error_message': "You didn't select a valid round.",
        })

    response = {
        'success' : True,
        'scores' : serializers.serialize('json', rnd.score_set.all())
    }
    

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    # Send user to the round view to add players/track scores
    return JsonResponse(response)