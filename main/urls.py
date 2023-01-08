
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.contrib.auth import views as auth_views 

#path('accounts/', include('django.contrib.auth.urls')),

urlpatterns = [
    path('',views.landing),
    path('register',views.register),
    path('register/teacher', views.registerT),
    path('class/join', views.JoinClass),
    path('login', views.loginn),
    path('dashboard',views.dashboard),
    path('dashboard/teacher',views.dashboardT),
    path('logout', views.logoutt),
    path('profile/<id>',views.profiles),
 #   path('book/<id>', views.bookView),
    path('search/<q>', views.search),
    path('class/send', views.sendBook),
    path('class/book/<id>', views.bookPage),
    path('book/read/<id>',views.book),
    path('book/progress/report', views.progress),
    path('leaderboards', views.leaderboard),
    path('class', views.classView),
    path('class/student/<id>', views.StudentView),
    path('request/goal', views.read_goal),
    path('accounts/', include('django.contrib.auth.urls')),
    path('password_reset/done/', auth_views.PasswordResetView.as_view(template_name='password-reset.html'), name='password_reset_done'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
