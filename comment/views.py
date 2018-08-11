from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from .models import Comment

@login_required
def update_comment(request):
    user = request.user
    text = request.POST.get('context','').strip()
    refer = request.META.get('HTTP_REFERER', '/')
    try:
        content_type = request.POST.get('content_type', '')
        object_id = int(request.POST.get('object_id', ''))
        modle_class = ContentType.objects.get(model=content_type).model_class()
        model_obj = modle_class.objects.get(pk=object_id)
    except Exception as e:
        return redirect(refer)

    comment = Comment()
    comment.user = user
    comment.text = text
    comment.content_object = model_obj
    comment.save()
    return redirect(refer)

