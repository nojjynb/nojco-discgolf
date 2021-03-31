from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'scorecard'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('round/<int:pk>/', views.RoundView.as_view(), name='round'),
    path('hole/<int:pk>/', views.HoleView.as_view(), name='hole'),
    path('new_round', views.new_round, name='new_round'),
    path('add_player_to_round/<int:roundid>/<int:playerid>', views.add_player_to_round, name='add_player_to_round'),
    path('save_scores/<int:roundid>', views.save_scores, name='save_scores'),
    path('previous_rounds', views.PreviousRounds.as_view(), name='previous_rounds'),
    path('complete_round/<int:roundid>', views.complete_round, name='complete_round'),
    path('delete_round/<int:roundid>', views.delete_round, name='delete_round'),
    path('current_round', views.current_round, name='current_round'),
    path('calculate_handicaps', views.calculate_handicaps, name='calculate_handicaps'),
    path('player_handicaps', views.PlayerHandicaps.as_view(), name='player_handicaps'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)