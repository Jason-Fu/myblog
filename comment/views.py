from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from .models import Comment
from .forms import CommentForm
from django.http import JsonResponse

@login_required
def update_comment(request):
    comment_form = CommentForm(request.POST,user=request.user)
    data = {}
    if comment_form.is_valid():
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']

        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user

        comment.save()
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.username
        data['text'] = comment.text
        data['comment_time'] = comment.comment_time.timestamp()
        data['content_type'] = ContentType.objects.get_for_model(comment).model
        if not parent is None:
            data['reply_to'] = comment.reply_to.username
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
    else:
        data['status'] = 'ERROR'
        data['error_message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)

