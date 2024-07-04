#urls.py file for the app library

from django.urls import path
from . import views

urlpatterns = [
    path("login1", views.index, name = "index"),
    path("login2", views.login2, name = "login2"),
    path("error", views.index, name = "error"),
    path("admin", views.admin, name = "admin"),
    path("student", views.student, name = "student"),
    path("books", views.booklist, name ="books"),
    path("student_details", views.studetails, name = "student_details"),
    path("borrow", views.borrow, name = "borrow"),
    path("addbook", views.addbook, name = "addbook"),
    path("addstudent", views.addstudent, name = "addstudent"),
    path("addborrow", views.addborrow, name = "addborrow"),
    path("addborjm", views.addborjm, name = "addborjm"),
    path("updborrow", views.updborrow, name = "updborrow"),
    path("addjm", views.addjm, name = "addjm"),
    path("trending", views.trending, name = "trending"),
    path("booksstu", views.booksstu, name = "booksstu"),
]