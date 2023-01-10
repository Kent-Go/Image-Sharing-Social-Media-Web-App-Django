from django import forms
from .models import Comment

# Create ModelForm for user to make new post
class CommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Comment'}), required=True)

    class Meta:
        model = Comment
        fields = ['body']