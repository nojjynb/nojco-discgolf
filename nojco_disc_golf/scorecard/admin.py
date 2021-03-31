from django.contrib import admin

# Register your models here.
from .models import Player,Round,Hole,Course, Score

admin.site.register(Course)
admin.site.register(Round)
admin.site.register(Player)
admin.site.register(Hole)
admin.site.register(Score)