from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('all-cities/', views.allCities, name='allCities'),
    #path('all-cities-index/', views.all_cities_index, name='allCitiesIndex'),
    #path("update-cities/", views.update_cities, name="update_cities"),
    path('analysis/', views.analysis, name='analysis'),
    path('safety/', views.safety, name='safety'),
    path('about/', views.about, name='about'),   
]

