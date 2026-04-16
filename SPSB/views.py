from django.shortcuts import render, get_object_or_404, redirect
from .models import NewsPost, Category, Media, NewsPostMedia
from .forms import NewsPostForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

from django.utils import timezone
from .forms import NewsPostForm, NewsPostMediaFormSet

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
def create_or_edit_post(request, pk=None):
    post = get_object_or_404(NewsPost, pk=pk) if pk else None

    if request.method == 'POST':
        form = NewsPostForm(request.POST, instance=post)
        formset = NewsPostMediaFormSet(request.POST, instance=post)

        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user

            if form.cleaned_data.get('publish_now'):
                post.status = 'published'
                post.published_at = timezone.now()

            post.save()
            formset.save()

            return redirect('news')

    else:
        form = NewsPostForm(instance=post)
        formset = NewsPostMediaFormSet(instance=post)

    return render(request, 'news_form.html', {
        'form': form,
        'formset': formset
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


def logout_view(request):
    logout(request)
    messages.error(request, "You have been logged out.")
    return redirect('home')

