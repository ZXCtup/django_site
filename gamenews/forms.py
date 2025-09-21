from django import forms
from django.forms import widgets

from gamenews.models import Post

class AddPostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'

    def clean_views(self):
        if 0 > self.cleaned_data["views"] > 0 :
            raise forms.ValidationError('Просмотры нельзя изменять')
        return self.cleaned_data["views"]

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control bg-dark text-light border-secondary exo',
        'rows': 3,
        'placeholder': 'Ваш комментарий...',
    }), label='')
















    # title = forms.CharField(max_length=50)
    # slug = forms.SlugField(max_length=70)

    # def clean_title(self):
    #     title = self.cleaned_data["title"]
    #     if title == 'XXX':
    #         raise forms.ValidationError('Нельзя вводить XXX')
    #     return title

