import datetime
from django.db import models
from django.utils import timezone
from address.models import AddressField
from nojco_disc_golf.users.models import User
from django.db.models import signals

# Create your models here.
    
class Player(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(null=True)
    handicap = models.IntegerField(default=36)
    handicap_date = models.DateTimeField('date', auto_now_add=True)
    best_round_id = models.IntegerField(null=True)
    best_delta = models.IntegerField(null=True)
    rounds_counted = models.IntegerField(null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name
    
    class Meta:
            ordering = ['name']

class Course(models.Model):
    name = models.CharField(max_length=200)
    location = AddressField(null=True)
    par = models.IntegerField(default=56)
    slope = models.IntegerField(default=0)
    holes = models.IntegerField(default=18)
    def __str__(self):
        return self.name

    class Meta:
            ordering = ['name']

class Round(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    date = models.DateTimeField('date')
    par = models.IntegerField(default=56)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.title
    def fancy_title(self):
        fancy_title = self.course.name
        if (self.title != fancy_title):
            fancy_title = self.title + " (" + fancy_title + ")"
        fancy_title = fancy_title + " - " + self.date.strftime("%m/%d/%Y")
        return fancy_title
    class Meta:
            ordering = ['-date']
    
class Hole(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    hole_num = models.IntegerField(default=0)
    par = models.IntegerField(default=3)
    distance = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return str(self.hole_num)
    
    class Meta:
            ordering = ['hole_num']
    
class CourseHole(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    hole_num = models.IntegerField(default=0)
    par = models.IntegerField(default=3)
    distance = models.IntegerField(null=True, blank=True)
    
    class Meta:
            ordering = ['hole_num']
    
class Score(models.Model):
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    class Meta:
            ordering = ['hole__hole_num', 'player__name']

class RoundPlayers(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    handicap = models.IntegerField(default=36)
    class Meta:
            ordering = ['player__name']

class HistoricalHandicaps(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    handicap = models.IntegerField(default=36)
    handicap_date = models.DateTimeField('date')

class UserFriends(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)



def user_post_save(sender, instance, created, *args, **kwargs):
    """Argument explanation:

       sender - The model class. (User)
       instance - The actual instance being saved.
       created - Boolean; True if a new record was created.

       *args, **kwargs - Capture the unneeded `raw` and `using`(1.3) arguments.
    """
    if created:
        try:
            players = Player.objects.filter(name__icontains=instance.username)
            player = players.first()
        except (KeyError, Player.DoesNotExist):
            player = instance.player_set.create(name=instance.username)
    elif instance.username == 'admin':
        return
    else:
        
        try:
            player = Player.objects.get(user=instance)
            player.name = instance.name
            player.save()
        except:
            try:
                players = Player.objects.filter(name__icontains=instance.username)
                player = players.first()
                player.user = instance
                player.save()
            except (KeyError, Player.DoesNotExist):
                player = Player.objects.create(name=instance.username)

signals.post_save.connect(user_post_save, sender=User)
    