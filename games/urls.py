from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.create_post, name='create_post'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('request/<int:pk>/<str:action>/', views.manage_request, name='manage_request'),
    path('register/', views.register, name='register'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/toggle/', views.toggle_post, name='toggle_post'),
    path('profile/<str:username>/', views.player_profile, name='player_profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/<int:pk>/', views.mark_read, name='mark_read'),
    path('rate/<str:username>/<int:post_pk>/', views.rate_player, name='rate_player'),
    path('search/', views.search_players, name='search_players'),
]
