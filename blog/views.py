from django.shortcuts import render_to_response,get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from read_statistics.utils import read_statistics_once,get_7days_read_num
from .models import BlogType,Blog

def blog_list(request):
    all_blogs = Blog.objects.all()
    context = get_common_blogs_data(request,all_blogs)
    return render_to_response('blog_list.html',context)


def blog_detail(request,blog_pk):
    currentBlog = get_object_or_404(Blog, id=blog_pk)
    key = read_statistics_once(request,currentBlog)
    context = {}

    previous_blog = Blog.objects.filter(create_time__gt=currentBlog.create_time).last()
    next_blog=Blog.objects.filter(create_time__lt=currentBlog.create_time).first()
    context['blog'] = currentBlog
    context['previous_blog']=previous_blog
    context['next_blog']=next_blog
    response = render_to_response('blog_detail.html', context)
    response.set_cookie(key,'true')
    return response

def blog_with_type(request,blog_with_type):
    blog_type = get_object_or_404(BlogType, id=blog_with_type)
    all_blogs = Blog.objects.filter(blog_type=blog_type)
    context=get_common_blogs_data(request,all_blogs)
    context['blog_type'] = blog_type
    return render_to_response('blog_with_type.html', context)

def index(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates,read_nums = get_7days_read_num(blog_content_type)
    context = {}
    context['read_num'] = read_nums
    context['dates'] = dates
    return render_to_response('index.html',context)

def blog_with_date(request,year,month):
    all_blogs = Blog.objects.filter(create_time__year=year,create_time__month=month)
    context = get_common_blogs_data(request,all_blogs)
    context['blog_with_date'] = '%s年%s月' %(year,month)
    context['blogs'] = all_blogs
    return render_to_response('blog_with_date.html', context)

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