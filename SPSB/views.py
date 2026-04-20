from cherrypy import request
from django.http import JsonResponse
from django.db import transaction

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


from django.core.paginator import Paginator

def news(request):
    category_filter = request.GET.get('category')
    categories = Category.objects.all()

    if request.user.is_staff:
        # Admin sees everything
        news_posts = NewsPost.objects.select_related('category').prefetch_related('post_media__media')
    else:
        # Visitors see only published
        news_posts = NewsPost.objects.filter(status='published').select_related('category').prefetch_related('post_media__media')

    if category_filter:
        news_posts = news_posts.filter(category__name=category_filter)

    # Pagination
    paginator = Paginator(news_posts, 9)  # Show 9 news per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news.html', {
        'page_obj': page_obj,
        'news_posts': page_obj.object_list,  # Keep backward compatibility
        'categories': categories,
        'selected_category': category_filter,
    })


@login_required
def upload_media(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        media = Media.objects.create(
            file=file,
            uploaded_by=request.user
        )

        return JsonResponse({
            'success': True,
            'id': media.id,
            'url': media.file.url
        })

    return JsonResponse({'success': False}, status=400)


@login_required
def media_list(request):
    media_items = Media.objects.filter(is_active=True)
    data = [
        {
            'id': media.id,
            'url': media.file.url,
            'caption': media.caption or ''
        }
        for media in media_items
    ]
    return JsonResponse(data, safe=False)


@login_required
def create_or_edit_post(request, pk=None):
    post = get_object_or_404(NewsPost, pk=pk) if pk else None

    if request.method == 'POST':
        form = NewsPostForm(request.POST, request.FILES, instance=post)
        formset = NewsPostMediaFormSet(request.POST, request.FILES, instance=post)

        if form.is_valid() and formset.is_valid():

            with transaction.atomic():

                post = form.save(commit=False, user=request.user)
                
                if form.cleaned_data.get('publish_now'):
                    post.status = 'published'
                    post.published_at = timezone.now()

                post.save()

                formset.instance = post

                for deleted_form in formset.deleted_forms:
                    if deleted_form.instance.pk:
                        deleted_form.instance.delete()

                for form_item in formset.forms:
                    if form_item.cleaned_data.get('DELETE'):
                        continue

                    if not form_item.has_changed() and not form_item.instance.pk:
                        continue

                    instance = form_item.save(commit=False)
                    section_image = form_item.cleaned_data.get('section_image')
                    selected_media = form_item.cleaned_data.get('media')

                    if section_image:
                        media_obj = Media.objects.create(file=section_image, uploaded_by=request.user)
                        instance.media = media_obj
                    elif selected_media:
                        instance.media = selected_media

                    instance.post = post
                    instance.save()

            if post.status == 'published':
                messages.success(request, f"Post {post.status.capitalize()} Successfully!")
            elif post.status == 'draft':
                messages.warning(request, f"Post {post.status.capitalize()} Successfully!")
            else:
                messages.info(request, f"Post {post.status.capitalize()} Successfully!")
            return redirect('news')

        else:
            messages.error(request, f"{form.errors} {formset.errors}")

    else:
        form = NewsPostForm(instance=post)
        formset = NewsPostMediaFormSet(instance=post)

    return render(request, 'news_form.html', {
        'form': form,
        'formset': formset
    })

def article(request, id):
    post = get_object_or_404(NewsPost, id=id)

    if post.status != 'published' and not request.user.is_staff:
        messages.error(request, "This article is not available.")
        return redirect('news')

    return render(request, 'article.html', {
        'post': post
    })

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_posts = NewsPost.objects.filter(created_by=request.user)

    return render(request, 'dashboard.html', {
        'user_posts': user_posts
    })


@login_required
def delete_post(request, id):
    post = NewsPost.objects.get(id=id)

    if request.method == 'POST':
        post.delete()
        messages.error(request, "Post Deleted and Never be Recovered!")
    
    return redirect('news')

    

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
                return redirect('news')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.error(request, "You have been logged out.")
    return redirect('home')



