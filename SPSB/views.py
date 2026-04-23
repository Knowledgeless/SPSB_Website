from django.http import JsonResponse
from django.db import transaction
import pandas as pd
from django.db.models import Q
import os 
from django.conf import settings
from django.core.files import File

from django.shortcuts import render, get_object_or_404, redirect
from .models import NewsPost, Category, Media, NewsPostMedia, Volunteer, CommitteeMember
from .forms import NewsPostForm
from django.views.decorators.cache import never_cache
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

@never_cache
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
    paginator = Paginator(news_posts, 9)  # Show 12 news per page
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

@never_cache
def article(request, id):
    post = get_object_or_404(NewsPost, id=id)

    if post.status != 'published' and not request.user.is_staff:
        messages.error(request, "This article is not available.")
        return redirect('news')

    # Get published posts filter
    published_filter = NewsPost.objects.filter(status='published')
    if not request.user.is_staff:
        published_posts = published_filter
    else:
        published_posts = NewsPost.objects.all()

    # Same category news (5 recent)
    same_category_posts = published_posts.filter(
        category=post.category
    ).exclude(id=post.id).order_by('-created_at')[:5]

    # Recent news (5 most recent)
    recent_posts = published_posts.exclude(id=post.id).order_by('-created_at')[:5]

    # Get banner image (the one marked as banner)
    banner_image = post.post_media.filter(is_banner=True).first()

    # Get banner image (the one marked as banner)
    banner_image = post.post_media.filter(is_banner=True).first()

    # Get caption: from banner if exists, else from first section image
    if banner_image:
        caption = banner_image.media.caption if banner_image.media.caption else ''
    else:
        first_section = post.post_media.filter(is_banner=False).first()
        caption = first_section.media.caption if first_section and first_section.media.caption else ''

    return render(request, 'article.html', {
        'post': post,
        'banner_image': banner_image,
        'same_category_posts': same_category_posts,
        'recent_posts': recent_posts,
        "caption": caption,
    })


def volunteers(request):
    volunteers = Volunteer.objects.filter(is_public=True)

    # SEARCH
    search = request.GET.get('search')
    if search:
        volunteers = volunteers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(username__icontains=search)
        )

    # YEAR FILTER
    selected_year = request.GET.get('year')
    if selected_year:
        volunteers = volunteers.filter(volunteer_year=selected_year)

    # PAGINATION
    paginator = Paginator(volunteers.order_by('-volunteer_year'), 12)  # 12 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # YEARS
    volunteer_year = Volunteer.objects.values_list(
        'volunteer_year', flat=True
    ).distinct().order_by('-volunteer_year')
    # print(page_obj.object_list.query)  # Debugging: Check the final query
    return render(request, 'volunteers.html', {
        'page_obj': page_obj,
        'volunteer_year': volunteer_year,
        'selected_year': selected_year
    })

def clean_value(value, default='-'):
    """
    Handles NaN, empty, None safely
    """
    if pd.isna(value):
        return default
    value = str(value).strip()
    return value if value else default


@login_required
def upload_volunteers_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']

        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, "Only .xlsx files are allowed!")
            return redirect('volunteers')

        try:
            df = pd.read_excel(excel_file)

            # ✅ Required columns
            required_columns = [
                'username', 'first_name', 'last_name',
                'email', 'volunteer_year', 'image_path'   # 🔥 ADD THIS COLUMN
            ]

            for col in required_columns:
                if col not in df.columns:
                    messages.error(request, f"Missing column: {col}")
                    return redirect('volunteers')

            created_count = 0
            skipped_count = 0
            duplicate_count = 0

            with transaction.atomic():
                for _, row in df.iterrows():

                    username = clean_value(row.get('username'), default='')
                    email = clean_value(row.get('email'), default='')

                    if not username:
                        skipped_count += 1
                        continue

                    if Volunteer.objects.filter(username=username).exists():
                        duplicate_count += 1
                        continue

                    try:
                        volunteer_year = int(row.get('volunteer_year', 2025))
                    except:
                        volunteer_year = 2025

                    # 🔥 CREATE OBJECT FIRST
                    volunteer = Volunteer(
                        username=username,
                        first_name=clean_value(row.get('first_name')),
                        last_name=clean_value(row.get('last_name')),
                        email=email if email != '-' else f"{username}@example.com",
                        volunteer_year=volunteer_year,

                        role=clean_value(row.get('role')),
                        institution=clean_value(row.get('institution')),
                        degree=clean_value(row.get('degree')),
                        phone_number=clean_value(row.get('phone_number')),

                        is_public=True,
                        status='active',
                        added_by=request.user
                    )

                    # 🔥 IMAGE HANDLING
                    image_path = clean_value(row.get('image_path'), default='')

                    if image_path and image_path != '-':
                        full_path = os.path.join(settings.MEDIA_ROOT, image_path)

                        if os.path.exists(full_path):
                            with open(full_path, 'rb') as img_file:
                                volunteer.profile_image.save(
                                    os.path.basename(full_path),
                                    File(img_file),
                                    save=False
                                )
                        else:
                            print(f"Image not found: {full_path}")

                    # 🔥 IMPORTANT: SAVE INDIVIDUALLY
                    volunteer.save()
                    created_count += 1

            messages.success(
                request,
                f"Upload Complete → Created: {created_count}, Skipped: {skipped_count}, Duplicates: {duplicate_count}"
            )

        except Exception as e:
            messages.error(request, f"Upload failed: {str(e)}")

        return redirect('volunteers')

    return redirect('volunteers')

def committees(request):
    committees = CommitteeMember.objects.filter(is_public=True)
    return render(request, 'committees.html', {'committees': committees})

@login_required
def upload_committee_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']

        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, "Only .xlsx files are allowed!")
            return redirect('committees')

        try:
            df = pd.read_excel(excel_file)

            required_columns = ['username', 'first_name', 'last_name', 'email', 'committee_year']

            for col in required_columns:
                if col not in df.columns:
                    messages.error(request, f"Missing column: {col}")
                    return redirect('committees')

            members_to_create = []

            with transaction.atomic():
                for _, row in df.iterrows():

                    username = str(row.get('username', '')).strip()
                    email = str(row.get('email', '')).strip()

                    if not username:
                        continue

                    if CommitteeMember.objects.filter(username=username).exists():
                        continue

                    member = CommitteeMember(
                        username=username,
                        first_name=row.get('first_name', '-') or '-',
                        last_name=row.get('last_name', '-') or '-',
                        email=email if email else f"{username}@example.com",
                        committee_year=int(row.get('committee_year', 2025)),

                        position=row.get('position', 'member'),
                        department=row.get('department', '-'),
                        phone_number=row.get('phone_number', '-'),

                        added_by=request.user
                    )

                    members_to_create.append(member)

                CommitteeMember.objects.bulk_create(members_to_create)

            messages.success(request, f"{len(members_to_create)} Committee members uploaded!")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect('committees')

    return redirect('committees')


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

    
@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('news')
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

@never_cache
@login_required
def logout_view(request):
    logout(request)
    messages.error(request, "You have been logged out.")
    return redirect('home')


