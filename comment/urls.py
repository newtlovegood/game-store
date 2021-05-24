from django.urls import path
from .views import comment_post, delete_comment


app_name = 'comments'

urlpatterns = [
    path('', comment_post, name='comment-post'),
    path('delete/', delete_comment, name='comment-delete'),
]

