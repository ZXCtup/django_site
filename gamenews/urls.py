from django.contrib import admin
from django.urls import path

from gamenews.views import IndexPage, AddPostView, DetailPost, UpdatePostView, CategoryView, CategoryDetailView

urlpatterns = [
    path('', IndexPage.as_view(), name='home'),

    path('post/<slug:slug>/', DetailPost.as_view(), name='post'),
    path('post_update/<slug:slug>/', UpdatePostView.as_view(), name='post_update'),
    path('post_add/', AddPostView.as_view() , name='post_add'),

    path('category/<slug:slug>/', CategoryDetailView.as_view(), name="category"),
    path('category/', CategoryView.as_view(), name="category_all"),

    
]
