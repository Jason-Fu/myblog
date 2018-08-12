from django.shortcuts import render_to_response,get_object_or_404,render
from django.core.paginator import Paginator
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from read_statistics.utils import *
from .models import BlogType,Blog
from comment.models import Comment
from comment.forms import CommentForm

def blog_list(request):
    all_blogs = Blog.objects.all()
    context = get_common_blogs_data(request,all_blogs)
    return render(request,'blog_list.html',context)


def blog_detail(request,blog_pk):
    currentBlog = get_object_or_404(Blog, id=blog_pk)
    key = read_statistics_once(request,currentBlog)
    blog_content_type = ContentType.objects.get_for_model(currentBlog)
    comments = Comment.objects.filter(content_type= blog_content_type,object_id=blog_pk,parent=None)
    context = {}

    previous_blog = Blog.objects.filter(create_time__gt=currentBlog.create_time).last()
    next_blog=Blog.objects.filter(create_time__lt=currentBlog.create_time).first()
    context['blog'] = currentBlog
    context['previous_blog']=previous_blog
    context['next_blog']=next_blog
    context['comments'] = comments.order_by('-comment_time')
    context['comment_form'] = CommentForm(initial={'content_type':blog_content_type.model,'object_id':blog_pk,'reply_comment_id':0 })
    response = render(request,'blog_detail.html', context)
    response.set_cookie(key,'true')
    return response

def blog_with_type(request,blog_with_type):
    blog_type = get_object_or_404(BlogType, id=blog_with_type)
    all_blogs = Blog.objects.filter(blog_type=blog_type)
    context=get_common_blogs_data(request,all_blogs)
    context['blog_type'] = blog_type
    return render(request,'blog_with_type.html', context)

def index(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates,read_nums = get_7days_read_num(blog_content_type)
    today_hottest_blog = get_hottest_blog_By_day(blog_content_type)
    yesterday_hottest_blog = get_yesterday_hottes_blog(blog_content_type)
    weekly_hottest_blog = cache.get('weekly_hottest_blog')
    if weekly_hottest_blog is None:
        weekly_hottest_blog = weekly_hottest_blogs()
        cache.set('weekly_hottest_blog',weekly_hottest_blog,3600)
    context = {}
    context['read_num'] = read_nums
    context['dates'] = dates
    context['today_hottest_blog'] = today_hottest_blog
    context['yesterday_hottest_blog'] = yesterday_hottest_blog
    context['weekly_hottest_blog'] = weekly_hottest_blog
    return render(request,'index.html', context)

def blog_with_date(request,year,month):
    all_blogs = Blog.objects.filter(create_time__year=year,create_time__month=month)
    context = get_common_blogs_data(request,all_blogs)
    context['blog_with_date'] = '%s年%s月' %(year,month)
    context['blogs'] = all_blogs
    return render(request,'blog_with_date.html', context)

def get_common_blogs_data(request,all_blogs):
    p = Paginator(all_blogs, 4)
    page_num = request.GET.get('page', 1)
    page_of_blogs = p.get_page(page_num)
    current_page = page_of_blogs.number
    page_list = list(range(max(current_page - 2, 1), current_page)) + \
                list(range(current_page, min(current_page + 2, p.num_pages) + 1))
    if page_list[0] - 1 >= 2:
        page_list.insert(0, '...')
    if p.num_pages - page_list[-1] >= 2:
        page_list.append('...')

    if page_list[0] != 1:
        page_list.insert(0, 1)
    if page_list[-1] != p.num_pages:
        page_list.append(p.num_pages)

    blogs_date=Blog.objects.dates('create_time', 'month', order='DESC')
    blogs_date_dict={}
    for blog_date in blogs_date:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year, create_time__month=blog_date.month).count()
        blogs_date_dict[blog_date] = blog_count
    context = {}
    context['p'] = p
    context['page_of_blogs'] = page_of_blogs
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['page_list'] = page_list
    context['blogs_date'] = blogs_date_dict
    return context

def weekly_hottest_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today,read_details__date__gte=date).values('id','title').annotate(sum=Sum('read_details__read_number')).order_by('-sum')
    return blogs[:7]