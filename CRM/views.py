from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Все кайф ежжи!")
            return redirect('login')
        else:
            messages.success(request, "Неверный логин и/или пароль!")
            return redirect('login')
    else:
        return render(request, template_name='login.html', context={})
