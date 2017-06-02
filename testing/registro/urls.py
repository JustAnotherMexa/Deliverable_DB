from django.conf.urls import include, url
from registro import views
from django.contrib.auth.views import login

urlpatterns =[
    url('^$', views.registro),
]