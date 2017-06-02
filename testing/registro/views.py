from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from registro.forms import UserRegistration
from django.conf import settings
from django.db import connection
import cx_Oracle
# Create your views here.

def registro(request):
    if request.method == 'POST':
        form = UserRegistration(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
    else:
        form = UserRegistration()
    return render(request, 'registro/registro.html', {'form':form})
