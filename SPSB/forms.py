from django import forms
from django.forms import inlineformset_factory
from .models import NewsPost, Media, NewsPostMedia


class NewsPostForm(forms.ModelForm):
    
    # Custom field to handle multiple media selection
    media_items = forms.ModelMultipleChoiceField(
        queryset=Media.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control'
        })
    )

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
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def save(self, commit=True, user=None):
        
        post = super().save(commit=False)

        if user:
            post.created_by = user

        if commit:
            post.save()

            # Handle ManyToMany through model manually
            media_items = self.cleaned_data.get('media_items')

            if media_items:
                for index, media in enumerate(media_items):
                    NewsPostMedia.objects.create(
                        post=post,
                        media=media,
                        order=index
                    )

        return post
    
