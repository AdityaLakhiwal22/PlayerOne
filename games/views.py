from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from .models import GamePost, JoinRequest, Comment, PlayerProfile
from .forms import GamePostForm, JoinRequestForm, CommentForm, RegisterForm, PlayerProfileForm, VenueForm
from .models import GamePost, JoinRequest, Comment, PlayerProfile, Notification, Reputation, Venue
import json

def home(request):
    posts = GamePost.objects.filter(status='open').select_related('posted_by')

    # Filters
    mode = request.GET.get('mode', '')
    sport = request.GET.get('sport', '')
    city = request.GET.get('city', '')
    search = request.GET.get('search', '')

    if mode:
        posts = posts.filter(mode=mode)
    if sport:
        posts = posts.filter(sport=sport)
    if city:
        posts = posts.filter(city__icontains=city)
    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )

    context = {
        'posts': posts,
        'sport_choices': GamePost.SPORT_CHOICES,
        'mode_choices': GamePost.MODE_CHOICES,
        'filters': {'mode': mode, 'sport': sport, 'city': city, 'search': search},
    }
    return render(request, 'games/home.html', context)


def post_detail(request, pk):
    post = get_object_or_404(GamePost, pk=pk)
    join_form = JoinRequestForm()
    comment_form = CommentForm()
    user_request = None

    if request.user.is_authenticated:
        user_request = JoinRequest.objects.filter(game_post=post, player=request.user).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        if 'join' in request.POST:
            if not user_request:
                join_form = JoinRequestForm(request.POST)
                if join_form.is_valid():
                    jr = join_form.save(commit=False)
                    jr.game_post = post
                    jr.player = request.user
                    jr.save()
                    Notification.objects.create(
                        user=post.posted_by,
                        message=f"{request.user.username} wants to join your post: {post.title}",
                        link=f"/post/{post.pk}/"
                    )
                    messages.success(request, "Join request sent! 🎉")
                    return redirect('post_detail', pk=pk)

        elif 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                c = comment_form.save(commit=False)
                c.game_post = post
                c.author = request.user
                c.save()
                return redirect('post_detail', pk=pk)

    context = {
        'post': post,
        'join_form': join_form,
        'comment_form': comment_form,
        'user_request': user_request,
        'join_requests': post.join_requests.all() if request.user == post.posted_by else None,
    }
    return render(request, 'games/post_detail.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = GamePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.posted_by = request.user
            post.save()
            messages.success(request, "Post created! Players will find you. 🏆")
            return redirect('post_detail', pk=post.pk)
    else:
        form = GamePostForm()
    return render(request, 'games/create_post.html', {'form': form})


@login_required
def manage_request(request, pk, action):
    """Accept or reject a join request"""
    jr = get_object_or_404(JoinRequest, pk=pk)
    if jr.game_post.posted_by != request.user:
        messages.error(request, "Not allowed.")
        return redirect('home')

    if action == 'accept':
        jr.status = 'accepted'
        messages.success(request, f"{jr.player.username} accepted! ✅")
    elif action == 'reject':
        jr.status = 'rejected'
        messages.warning(request, f"{jr.player.username} rejected.")
    jr.save()
    if action == 'accept':
        Notification.objects.create(
        user=jr.player,
        message=f"Your request to join '{jr.game_post.title}' was accepted! 🎉",
        link=f"/post/{jr.game_post.pk}/"
        )
    elif action == 'reject':
        Notification.objects.create(
        user=jr.player,
        message=f"Your request to join '{jr.game_post.title}' was not accepted.",
        link=f"/post/{jr.game_post.pk}/"
    )

    # Auto-close if full
    post = jr.game_post
    if post.is_full():
        post.status = 'full'
        post.save()

    return redirect('post_detail', pk=post.pk)


@login_required
def my_posts(request):
    posts = GamePost.objects.filter(posted_by=request.user)
    joined = JoinRequest.objects.filter(player=request.user).select_related('game_post')
    return render(request, 'games/my_posts.html', {'posts': posts, 'joined': joined})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            PlayerProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f"Welcome to Player One, {user.username}! 🎮")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def edit_profile(request):
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated! 💪")
            return redirect('player_profile', username=request.user.username)
    else:
        form = PlayerProfileForm(instance=profile)
    return render(request, 'games/edit_profile.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(GamePost, pk=pk)
    if post.posted_by != request.user:
        messages.error(request, "You can only edit your own posts.")
        return redirect('home')
    if request.method == 'POST':
        form = GamePostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated! ✅")
            return redirect('post_detail', pk=post.pk)
    else:
        form = GamePostForm(instance=post)
    return render(request, 'games/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(GamePost, pk=pk)
    if post.posted_by != request.user:
        messages.error(request, "You can only delete your own posts.")
        return redirect('home')
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect('my_posts')
    return render(request, 'games/delete_post.html', {'post': post})

@login_required
def toggle_post(request, pk):
    post = get_object_or_404(GamePost, pk=pk)
    if post.posted_by != request.user:
        messages.error(request, "Not allowed.")
        return redirect('home')
    if post.status == 'closed':
        post.status = 'open'
        messages.success(request, "Post reopened! 🔓 Players can join again.")
    else:
        post.status = 'closed'
        messages.success(request, "Post closed. 🔒")
    post.save()
    return redirect('post_detail', pk=post.pk)

def player_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = PlayerProfile.objects.get_or_create(user=profile_user)
    posts = GamePost.objects.filter(posted_by=profile_user).order_by('-created_at')
    total_joins = JoinRequest.objects.filter(game_post__posted_by=profile_user, status='accepted').count()
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'total_joins': total_joins,
    }
    return render(request, 'games/player_profile.html', context)

@login_required
def notifications(request):
    notifs = Notification.objects.filter(user=request.user)
    unread = notifs.filter(is_read=False)
    unread.update(is_read=True)  # Mark all as read when page is opened
    return render(request, 'games/notifications.html', {'notifs': notifs})


@login_required
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect(notif.link or 'home')

@login_required
def rate_player(request, username, post_pk):
    rated_user = get_object_or_404(User, username=username)
    post = get_object_or_404(GamePost, pk=post_pk)

    # Can't rate yourself
    if rated_user == request.user:
        messages.error(request, "You can't rate yourself!")
        return redirect('post_detail', pk=post_pk)

    # Check already rated
    already_rated = Reputation.objects.filter(
        given_by=request.user, given_to=rated_user, game_post=post
    ).exists()
    if already_rated:
        messages.error(request, "You already rated this player for this game.")
        return redirect('post_detail', pk=post_pk)

    if request.method == 'POST':
        score = int(request.POST.get('score', 5))
        comment = request.POST.get('comment', '')
        Reputation.objects.create(
            given_by=request.user,
            given_to=rated_user,
            game_post=post,
            score=score,
            comment=comment
        )
        # Update total reputation on profile
        profile, _ = PlayerProfile.objects.get_or_create(user=rated_user)
        profile.reputation = rated_user.received_reputations.count()
        profile.save()

        # Notify rated player
        Notification.objects.create(
            user=rated_user,
            message=f"{request.user.username} gave you {score}⭐ for '{post.title}'!",
            link=f"/profile/{rated_user.username}/"
        )
        messages.success(request, f"You rated {rated_user.username} {score}⭐!")
        return redirect('post_detail', pk=post_pk)

    return render(request, 'games/rate_player.html', {
        'rated_user': rated_user,
        'post': post,
    })

def search_players(request):
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    results = []

    if query or city:
        profiles = PlayerProfile.objects.select_related('user').all()
        if query:
            profiles = profiles.filter(
                Q(user__username__icontains=query) |
                Q(bio__icontains=query)
            )
        if city:
            profiles = profiles.filter(
                Q(city__icontains=city) |
                Q(area__icontains=city)
            )
        results = profiles

    return render(request, 'games/search_players.html', {
        'results': results,
        'query': query,
        'city': city,
    })

def map_view(request):
    posts = GamePost.objects.filter(
        mode='outdoor',
        status='open',
        city__isnull=False
    ).exclude(city='').select_related('posted_by')

    # Build data for map markers
    map_data = []
    for post in posts:
        map_data.append({
            'title': post.title,
            'sport': post.get_sport_display(),
            'location': post.location,
            'city': post.city,
            'date': str(post.play_date) if post.play_date else '',
            'players_needed': post.spots_left(),
            'skill': post.get_skill_level_display(),
            'url': f'/post/{post.pk}/',
            'posted_by': post.posted_by.username,
        })

    return render(request, 'games/map_view.html', {
        'posts': posts,
        'map_data_json': json.dumps(map_data),
    })


def venues_home(request):
    cities = Venue.objects.filter(is_verified=True).values_list('city', flat=True).distinct().order_by('city')
    total_venues = Venue.objects.filter(is_verified=True).count()
    venues = Venue.objects.filter(is_verified=True)
    grounds = Venue.objects.filter(venue_type='ground', is_verified=True).count()
    turfs = Venue.objects.filter(venue_type='turf', is_verified=True).count()
    all_venues = Venue.objects.filter(is_verified=True)

    venues_map_data = []
    for v in all_venues:
        venues_map_data.append({
            'name': v.name,
            'type': v.venue_type,
            'area': v.area,
            'city': v.city,
            'sports': v.get_sports_display(),
            'price': v.price_per_hour or v.entry_fee,
            'hours': v.opening_hours,
            'url': f'/venues/detail/{v.pk}/',
            'lat': v.latitude,
            'lng': v.longitude,
        })

    return render(request, 'games/venues_home.html', {
        'cities': cities,
        'total_venues': total_venues,
        'grounds': grounds,
        'turfs': turfs,
        'venues_map_json': json.dumps(venues_map_data),
    })


def venues_city(request, city):
    areas = Venue.objects.filter(
        city__iexact=city, is_verified=True
    ).values_list('area', flat=True).distinct().order_by('area')
    grounds_count = Venue.objects.filter(city__iexact=city, venue_type='ground', is_verified=True).count()
    turfs_count = Venue.objects.filter(city__iexact=city, venue_type='turf', is_verified=True).count()
    return render(request, 'games/venues_city.html', {
        'city': city,
        'areas': areas,
        'grounds_count': grounds_count,
        'turfs_count': turfs_count,
    })


def venues_area(request, city, area):
    venue_type = request.GET.get('type', '')
    venues = Venue.objects.filter(city__iexact=city, area__iexact=area, is_verified=True)
    if venue_type:
        venues = venues.filter(venue_type=venue_type)
    grounds = venues.filter(venue_type='ground')
    turfs = venues.filter(venue_type='turf')
    return render(request, 'games/venues_area.html', {
        'city': city,
        'area': area,
        'grounds': grounds,
        'turfs': turfs,
    })


def venue_detail(request, pk):
    venue = get_object_or_404(Venue, pk=pk)
    # Show active posts at this venue
    related_posts = GamePost.objects.filter(
        location__icontains=venue.name,
        status='open'
    )[:5]
    return render(request, 'games/venue_detail.html', {
        'venue': venue,
        'related_posts': related_posts,
    })


@login_required
def add_venue(request):
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.added_by = request.user
            venue.save()
            messages.success(request, f"{venue.name} added! ✅ It will be verified soon.")
            return redirect('venue_detail', pk=venue.pk)
    else:
        form = VenueForm()
    return render(request, 'games/add_venue.html', {'form': form})