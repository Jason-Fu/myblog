from django.contrib import auth
from django.shortcuts import redirect,render
from .forms import LoginForm,RegForm
from django.contrib.auth.models import User
from django.http import JsonResponse


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from'),'/')
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)

def login_for_medal(request):
    login_form = LoginForm(request.POST)
    data= {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            username = RegForm.cleaned_data['username']
            email = RegForm.cleaned_data['email']
            password = RegForm.cleaned_data['password']
            user = User.objects.create_user(username,email,password)
            user.save()
            user = auth.authenticate(username=username,password=password)
            auth.login(request,user)
            return redirect(request.GET.get('from'),'/')
    else:
        reg_form = RegForm()
    context = {}
    context['reg_form'] = reg_form
    return render(request, 'register.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from'), '/')

def user_info(request):
    context = {}
    return render(request,'user_info.html',context)