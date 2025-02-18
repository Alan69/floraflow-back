import requests
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

API_BASE_URL = 'https://api.floraflow.tech/api'

class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        response = requests.post(f'{API_BASE_URL}/login/', json={
            'email': email,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.json()
            # Store tokens in session
            request.session['access_token'] = data['access']
            request.session['refresh_token'] = data['refresh']
            return redirect('profile')
        else:
            messages.error(request, 'Неверный логин или пароль')
            return render(request, 'users/login.html')

class RegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        
        if password != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'users/register.html')
            
        response = requests.post(f'{API_BASE_URL}/register/', json={
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'city': city
        })
        
        if response.status_code == 201:
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('login')
        else:
            # Try to get more specific error message from the API response
            try:
                error_data = response.json()
                error_message = error_data.get('detail', 'Ошибка при регистрации')
                messages.error(request, error_message)
            except:
                messages.error(request, 'Ошибка при регистрации')
            return render(request, 'users/register.html')

class ProfileView(View):
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        # Get user profile from API
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.get(f'{API_BASE_URL}/me/', headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            return render(request, 'users/profile.html', {'user': user_data})
        else:
            messages.error(request, 'Ошибка при получении данных профиля')
            return redirect('login')

    def post(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        files = {}
        if request.FILES.get('profile_picture'):
            files['profile_picture'] = request.FILES['profile_picture']
            
        data = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone': request.POST.get('phone'),
            'city': request.POST.get('city'),
        }
        
        response = requests.patch(
            f'{API_BASE_URL}/me/',
            headers=headers,
            data=data,
            files=files
        )
        
        if response.status_code == 200:
            messages.success(request, 'Профиль успешно обновлен')
        else:
            messages.error(request, 'Ошибка при обновлении профиля')
            
        return redirect('profile') 