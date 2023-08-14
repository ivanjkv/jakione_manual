from django.urls import path
from . import views

urlpatterns = [
    path('', views.livescores, name='livescores'),
    path('fixtures/', views.fixtures, name='fixtures'),
    path('deadlines/', views.deadlines, name='deadlines'),
    path('match/<str:matchid>', views.match, name='match'),
    path('user/<str:userid>', views.user, name='user'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update_scores/', views.update_scores, name='update_scores'),
    path('upload_predictions/', views.upload_predictions, name='upload_predictions'),
    path('privacy/', views.privacy, name='privacy-policy'),
]
