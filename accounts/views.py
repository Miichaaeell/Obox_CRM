from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.generic import View


# Create your views here.
class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        username:str  = request.POST.get('username')
        password: str = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Usuário ou senha inválidos.'})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')
