from django.urls import path
from . import views
 
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('save-test-score/', views.save_test_score, name='save_test_score'),
]