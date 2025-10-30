from django.urls import path
from .views import formation_home ,  session_home , inscription_home , formateur_home , cours_programmes_home , formation_dashboard , configuration_home
from . import views  # ou from apps.formation import views

urlpatterns = [
   path('', formation_home, name='formation_home'),
   path('session/', session_home, name='session_home'),
   path('inscri/' , inscription_home, name='inscription_home'),
   path('formateur/' , formateur_home, name='formateur_home' ),
   path('cp/' , cours_programmes_home, name='cours_programmes_home' ),
   path('dashboard/' , formation_dashboard, name='formation_dashboard' ),
   path('config/' , configuration_home ,name='configuration_home'),

]
