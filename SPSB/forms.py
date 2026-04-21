from django import forms
from django.forms import inlineformset_factory
from .models import NewsPost, Media, NewsPostMedia


# =========================
# MAIN POST FORM
# =========================
class NewsPostForm(forms.ModelForm):
    
    publish_now = forms.BooleanField(required=False)
    new_category = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control mt-2',
        'placeholder': 'New Category'
    }))

    class Meta:
        model = NewsPost
        fields = [
            'title',
            'content',
            'category',
            'status',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write your content...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def save(self, commit=True, user=None):
        post = super().save(commit=False)

        new_category_name = self.cleaned_data.get('new_category')
        if new_category_name:
            from .models import Category
            category, _ = Category.objects.get_or_create(name=new_category_name)
            post.category = category

        if user:
            post.created_by = user

        if commit:
            post.save()

        return post


# =========================
# MEDIA SECTION FORM
# =========================
class NewsPostMediaForm(forms.ModelForm):

    # Allow the admin to upload a section image directly.
    section_image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={
        'class': 'form-control'
    }))

    media = forms.ModelChoiceField(
        queryset=Media.objects.all(),
        required=False
    )

    class Meta:
        model = NewsPostMedia
        fields = [
            'media',
            'caption_override',
            'section_text',
            'order',
            'is_banner'
        ]

        widgets = {
            'media': forms.HiddenInput(attrs={'class': 'media-id-input'}),
            'caption_override': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter caption'
            }),
            'section_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write section text...'
            }),
            'order': forms.HiddenInput(),
            'is_banner': forms.CheckboxInput(attrs={
                'class': 'form-check-input banner-checkbox'
            }),
        }


# =========================
# FORMSET
# =========================
NewsPostMediaFormSet = inlineformset_factory(
    NewsPost,
    NewsPostMedia,
    form=NewsPostMediaForm,
    extra=1,
    can_delete=True
)