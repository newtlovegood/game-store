from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from .forms import CommentForm, MPTTCommentForm
from .models import Comment, MPTTComment
from  games.models import Game


# Create your views here.
def comment_post(request):
    if request.POST.get('action') == 'post':
        # get comment data
        comment_content = request.POST.get('content')
        comment_parent = request.POST.get('parent')
        if not comment_parent:
            comment_parent = None
        else:
            comment_parent = get_object_or_404(MPTTComment, id=comment_parent)
        comment_game = request.POST.get('game')

        if request.user.is_authenticated:
            MPTTComment.objects.create(
                username=request.user,
                content=comment_content,
                parent=comment_parent,
                game=get_object_or_404(Game, id=comment_game),
            )
        else:
            MPTTComment.objects.create(
                content=comment_content,
                parent=comment_parent,
                game=get_object_or_404(Game, id=comment_game),
            )
        # return json
        return JsonResponse({'content': comment_content})


def delete_comment(request):
    if request.POST.get('action') == 'post':
        # get comment data
        comment_id = request.POST.get('id')
        get_object_or_404(MPTTComment, id=comment_id).delete()
        return JsonResponse({'message': 'Comment deleted'})
