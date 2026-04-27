from django.db import models
from django.contrib.auth.models import User


class PlayerProfile(models.Model):
    """Extended profile for each user/player"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True, help_text="Locality/Area e.g. Andheri, Bandra")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    reputation = models.IntegerField(default=0)  # Points from other players
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class GamePost(models.Model):
    """A post by a player looking for more players"""

    MODE_CHOICES = [
        ('outdoor', '🏏 Outdoor / Ground'),
        ('online', '🎮 Online / Game'),
    ]

    SPORT_CHOICES = [
        # Outdoor
        ('cricket', '🏏 Cricket'),
        ('football', '⚽ Football'),
        ('basketball', '🏀 Basketball'),
        ('volleyball', '🏐 Volleyball'),
        ('badminton', '🏸 Badminton'),
        ('kabaddi', '🤼 Kabaddi'),
        # Online
        ('bgmi', '🔫 BGMI'),
        ('valorant', '🎯 Valorant'),
        ('fifa', '⚽ FIFA'),
        ('chess', '♟️ Chess'),
        ('ludo', '🎲 Ludo'),
        ('other', '🎮 Other'),
    ]

    SKILL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('pro', 'Pro'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('full', 'Full'),
        ('closed', 'Closed'),
    ]

    # Who posted
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    # What they need
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES)
    title = models.CharField(max_length=200, help_text="e.g. Need 4 players for cricket at Azad Maidan")
    description = models.TextField(blank=True, help_text="Any extra details")

    # How many players needed
    players_have = models.PositiveIntegerField(default=1)
    players_needed = models.PositiveIntegerField(default=1)

    # Skill level
    skill_level = models.CharField(max_length=15, choices=SKILL_CHOICES, default='beginner')

    # For outdoor games
    location = models.CharField(max_length=200, blank=True, help_text="Ground/venue name")
    city = models.CharField(max_length=100, blank=True)
    play_date = models.DateField(null=True, blank=True)
    play_time = models.TimeField(null=True, blank=True)

    # For online games
    game_platform = models.CharField(max_length=50, blank=True, help_text="e.g. Mobile, PC, PS5")
    game_id = models.CharField(max_length=100, blank=True, help_text="Your in-game ID/username")

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def spots_left(self):
        joined = self.join_requests.filter(status='accepted').count()
        return self.players_needed - joined

    def is_full(self):
        return self.spots_left() <= 0


class JoinRequest(models.Model):
    """A player requesting to join a GamePost"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    game_post = models.ForeignKey(GamePost, on_delete=models.CASCADE, related_name='join_requests')
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='join_requests')
    message = models.TextField(blank=True, help_text="Why do you want to join?")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('game_post', 'player')  # Can't join same post twice

    def __str__(self):
        return f"{self.player.username} → {self.game_post.title}"


class Comment(models.Model):
    """Comments on a game post"""
    game_post = models.ForeignKey(GamePost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username} on {self.game_post.title}"
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notif for {self.user.username}: {self.message}"
