from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Create Airport Route
    path('add-route/', views.add_route, name='add_route'),
    
    # Question 1: Find Last Reachable Node
    path('find-last-reachable/', views.find_last_reachable, name='find_last_reachable'),
    
    # Question 2: Longest Duration
    path('longest-duration/', views.longest_duration, name='longest_duration'),
    
    # Question 3: Shortest Duration
    path('shortest-duration/', views.shortest_duration, name='shortest_duration'),
]