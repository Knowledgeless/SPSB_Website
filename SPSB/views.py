from django.shortcuts import render, redirect
from .models import NewsPost, Category, Media, NewsPostMedia
from .forms import NewsPostForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.
def home(request):
    return render(request, 'home.html')


def news(request):
    # news_posts = NewsPost.objects.prefetch_related('mediapost_set__media').all().order_by('-created_at')
    # news_posts = NewsPost.objects.prefetch_related('post_media__media').all()
    news_posts = NewsPost.objects.prefetch_related('post_media__media').all().order_by('-created_at')

    return render(request, 'news.html', {
        'news_posts': news_posts
    })


@login_required
def edit_post(request, id):
    post = NewsPost.objects.get(id=id)

    if request.method == 'POST':
        form = NewsPostForm(request.POST, instance=post)

        if form.is_valid():
            form.save(user=request.user)
            return redirect('news')
    else:
        form = NewsPostForm(instance=post)

    return render(request, 'edit_post.html', {
        'form': form,
        'post': post
    })


@login_required
def delete_post(request, id):
    post = NewsPost.objects.get(id=id)

    if request.method == 'POST':
        post.delete()
        return redirect('news')

    return render(request, 'delete_post.html', {
        'post': post
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})