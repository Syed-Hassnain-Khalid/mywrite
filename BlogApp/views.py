from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from .models import Blog
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.forms import ModelForm
import json

@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['user_name']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("index")
        else:
            return HttpResponse("Invalid credentials, please check your username and password")
    return render(request, 'login_signup.html', {'form': 'login'})

def handlesignup(request):
    if request.method == 'POST':
        name = request.POST['username']
        f_name = request.POST['first_name']
        l_name = request.POST['last_name']
        passw = request.POST['password']
        pass2 = request.POST['confirm_password']
        if len(passw) < 5:
            return HttpResponse("Password is too weak")
        if User.objects.filter(username=name).exists():
            return HttpResponse("Username already taken")
        if passw != pass2:
            return HttpResponse('Passwords do not match')
        
        myuser = User.objects.create_user(username=name, first_name=f_name, last_name=l_name, password=passw)
        myuser.save()
        return redirect('login')
    return render(request, 'login_signup.html', {'form': 'signup'})

def login_signup(request):
    return render(request, 'login_signup.html', {'form': 'login'})

@login_required(login_url='login')
def handlelogout(request):
    logout(request)
    return redirect('index')

@login_required(login_url='login')
def readblog(request):
    blog_list = Blog.objects.all().order_by('-created_at')
    paginator = Paginator(blog_list, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'blogs': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'readblog.html', context)

@login_required(login_url='login')
def add_blog(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if not title or not content:
            return HttpResponse("Title and Content are required.")
        blog = Blog(title=title, content=content, author=request.user)
        blog.save()
        return redirect('readblog')
    return render(request, 'add_blog.html')

@login_required(login_url='login')
def my_blog(request):
    blog_list = Blog.objects.filter(author=request.user).order_by('-created_at')
    paginator = Paginator(blog_list, 5)  # Show 5 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'blogs': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'my_blog.html', context)

# Create a ModelForm for Blog (Not used in JSON parsing, but kept for potential future use)
class BlogForm(ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content']

@login_required(login_url='login')
@require_POST
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        if not title or not content:
            return JsonResponse({'success': False, 'errors': 'Title and content cannot be empty.'})

        blog.title = title
        blog.content = content
        blog.save()

        # Optionally, return formatted date and excerpt
        return JsonResponse({
            'success': True,
            'blog': {
                'title': blog.title,
                'author': blog.author.username,
                'created_at': blog.created_at.strftime('%B %d, %Y'),
                'excerpt': blog.content[:50] + '...',  # Adjust truncate length as needed
                'content': blog.content,
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'errors': 'Invalid JSON data.'})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})

@login_required(login_url='login')
@require_POST
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    try:
        blog.delete()
        return JsonResponse({'success': True, 'message': 'Blog deleted successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})
