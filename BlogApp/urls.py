# BlogApp/urls.py

from django.urls import path
from BlogApp import views

urlpatterns = [
    path('', views.index, name='index'),
    path("login/", views.login_view, name="login"),
    path("signup/", views.handlesignup, name="handlesignup"),
    path("login_signup/", views.login_signup, name="login_signup"),
    path("logout/", views.handlelogout, name="logout"),
    path("readblog/", views.readblog, name="readblog"),
    path("add_blog/", views.add_blog, name="add_blog"),
    path("my_blog/", views.my_blog, name="my_blog"),  # Updated with trailing slash
    path("edit_blog/<int:blog_id>/", views.edit_blog, name="edit_blog"),  # Updated
    path("delete_blog/<int:blog_id>/", views.delete_blog, name="delete_blog"),  # Updated
]

#