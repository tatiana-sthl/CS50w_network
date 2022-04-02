from django import http
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import constraints
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
import json

from .models import User, Post, next_url, previous_url
from .forms import NewPostForm


def index(request):

    posts = Post.objects.all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "form": NewPostForm(),
        "page": page,
        "previous_url": previous_url(page),
        "next_url": next_url(page),
    })

@csrf_exempt
@login_required
def editpost(request, post_id):
    
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    try:
        post = Post.objects.get(pk = post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    # Edited only by the author
    if request.user == post.author:
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        content = body['content']

        Post.objects.filter(pk=post_id).update(content=f'{content}')

        return JsonResponse({"message": "Post updated successfully.", "content": content}, status=200)

    else:
        return JsonResponse({"error": "You do not have permission to do this"}, status=400)

        
@csrf_exempt
@login_required
def updatelike(request, post_id):
    
    user = request.user
    try:
        post = Post.objects.get(pk = post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    # Like and unlike post
    if (user.likes.filter(pk=post_id).exists()):
        post.liked_by.remove(user)
        likes_post = False
    else: 
        post.liked_by.add(user)
        likes_post = True
    likes = post.likes()
    
    return JsonResponse({"likesPost": likes_post, "likesCount": likes}, status=200)

@login_required
def newpost(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    form = NewPostForm(request.POST)

    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return HttpResponseRedirect(reverse("index"))

def profile(request, user_id):

    profile_user = User.objects.get(pk = user_id)

    profile_posts = Post.objects.filter(author=user_id)
    paginator = Paginator(profile_posts, 10)

    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    if request.user.is_authenticated:
        following = profile_user.followers.filter(id = request.user.id).exists()
    else:
        following = False

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "following": following,
        "following_count": profile_user.following.all().count(),
        "followers_count": profile_user.followers.all().count(),
        "page": page,
        "previous_url": previous_url(page),
        "next_url": next_url(page)
    })

@login_required(login_url='login')
def follow(request, user_to_follow):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    User.objects.get(pk=request.user.id).following.add(user_to_follow)
    return HttpResponseRedirect(reverse("profile", args=(user_to_follow,)))

@login_required(login_url='login')
def unfollow(request, user_to_unfollow):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    User.objects.get(pk=request.user.id).following.remove(user_to_unfollow)
    return HttpResponseRedirect(reverse("profile", args=(user_to_unfollow,)))

@login_required(login_url='login')
def following(request):
    
    following = User.objects.get(pk=request.user.id).following.all()

    following_ids = following.values_list('pk', flat=True)

    following_posts = Post.objects.filter(author__in=following_ids)    
    paginator = Paginator(following_posts, 10)

    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        "posts": following_posts,
        "page": page, 
        "previous_url": previous_url(page),
        "next_url": next_url(page)
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, 'Invalid username and/or password.')
            return render(request, "network/login.html")
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, 'Passwords must match.')
            return render(request, "network/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, 'Username already taken.')
            return render(request, "network/register.html")

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
