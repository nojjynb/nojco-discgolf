from django.contrib import admin

# Register your models here.
from .models import Player,Round,Hole,Course, Score, CourseHole, UserFriends
from nojco_disc_golf.users.models import User

class HoleInline (admin.TabularInline):
    model = CourseHole
    def get_extra(self, request, obj=None, **kwargs):
        extra = 18
        if obj:
            return extra - obj.coursehole_set.count()
        return extra

class CourseAdmin(admin.ModelAdmin):
    inlines = [HoleInline]

class ScoreInline (admin.TabularInline):
    model = Score
    fields = ["score", "player", "hole"]
    readonly_fields = ["hole", "player"]

class RoundAdmin(admin.ModelAdmin):
    inlines = [ScoreInline]

class UserFriendsInline (admin.StackedInline):
    model = UserFriends

class PlayerAdmin(admin.ModelAdmin):
    inlines = [UserFriendsInline]


admin.site.register(Course, CourseAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Player, PlayerAdmin)