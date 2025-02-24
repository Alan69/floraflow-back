import requests
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.conf import settings

API_BASE_URL = settings.BASE_URL + '/api'

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
            
            # Get user data and store it in session
            headers = {'Authorization': f'Bearer {data["access"]}'}
            user_response = requests.get(f'{API_BASE_URL}/me/', headers=headers)
            if user_response.status_code == 200:
                request.session['user_data'] = user_response.json()
            
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
            
            # Get payment history if available
            payment_history_response = requests.get(
                f'{API_BASE_URL}/payment/history/',
                headers=headers
            )
            
            payment_history = []
            if payment_history_response.status_code == 200:
                payment_history = payment_history_response.json()
                
            context = {
                'user': user_data,
                'payment_history': payment_history
            }
            
            return render(request, 'users/profile.html', context)
        else:
            messages.error(request, 'Ошибка при получении данных профиля')
            return redirect('login')

    def post(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        files = {}
        if request.FILES.get('profile_picture'):
            profile_pic = request.FILES['profile_picture']
            if profile_pic.size > 256 * 1024 * 1024:  # 256MB in bytes
                messages.error(request, 'Файл слишком большой. Максимальный размер: 256MB')
                return redirect('profile')
            files['profile_picture'] = profile_pic
            
        data = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone': request.POST.get('phone'),
            'city': request.POST.get('city'),
            'user_type': request.POST.get('user_type'),
        }
        
        response = requests.patch(
            f'{API_BASE_URL}/me/',
            headers=headers,
            data=data,
            files=files
        )
        
        if response.status_code == 200:
            # Update the session user data with the new information
            user_response = requests.get(f'{API_BASE_URL}/me/', headers=headers)
            if user_response.status_code == 200:
                request.session['user_data'] = user_response.json()
            
            messages.success(request, 'Профиль успешно обновлен')
            # If user type changed to store, redirect to store profile
            if data['user_type'] == 'store':
                return redirect('store_profile_update')
        else:
            messages.error(request, 'Ошибка при обновлении профиля')
            
        return redirect('profile')

class LogoutView(View):
    def get(self, request):
        # Clear the session
        request.session.pop('access_token', None)
        request.session.pop('refresh_token', None)
        request.session.pop('user_data', None)
        return redirect('index')

class StoreProfileView(View):
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.get(f'{API_BASE_URL}/store/profile/', headers=headers)
        
        if response.status_code == 200:
            store_data = response.json()
            context = {
                'store': store_data
            }
            return render(request, 'users/store_profile.html', context)
        else:
            messages.error(request, 'Ошибка при получении данных магазина')
            return redirect('profile')

    def post(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        
        # Prepare the files dictionary if there's a logo upload
        files = {}
        if request.FILES.get('logo'):
            files['logo'] = request.FILES['logo']
        
        # Prepare the data dictionary
        data = {
            'store_name': request.POST.get('store_name'),
            'address': request.POST.get('address'),
            'instagram_link': request.POST.get('instagram_link'),
            'twogis': request.POST.get('twogis'),
            'whatsapp_number': request.POST.get('whatsapp_number'),
        }
        
        # Make the API request
        response = requests.patch(
            f'{API_BASE_URL}/store/profile/',
            headers=headers,
            data=data,
            files=files
        )
        
        if response.status_code == 200:
            messages.success(request, 'Профиль магазина успешно обновлен')
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('detail', 'Ошибка при обновлении профиля магазина')
                messages.error(request, error_message)
            except:
                messages.error(request, 'Ошибка при обновлении профиля магазина')
        
        return redirect('store_profile')

class CreateOrderView(View):
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        
        # Get flowers list
        flowers_response = requests.get(f'{API_BASE_URL}/flowers/', headers=headers)
        colors_response = requests.get(f'{API_BASE_URL}/colors/', headers=headers)
        
        context = {
            'flowers': flowers_response.json() if flowers_response.status_code == 200 else [],
            'colors': colors_response.json() if colors_response.status_code == 200 else []
        }
        
        return render(request, 'orders/create_order.html', context)

    def post(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        
        data = {
            'flower': request.POST.get('flower'),
            'color': request.POST.get('color'),
            'flower_height': request.POST.get('flower_height'),
            'quantity': request.POST.get('quantity'),
            'decoration': request.POST.get('decoration') == 'on',
            'recipients_address': request.POST.get('recipients_address'),
            'recipients_phone': request.POST.get('recipients_phone'),
            'flower_data': request.POST.get('flower_data'),
        }
        
        response = requests.post(
            f'{API_BASE_URL}/client/order/',
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            messages.success(request, 'Заказ успешно создан')
            return redirect('profile')
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('detail', 'Ошибка при создании заказа')
                messages.error(request, error_message)
            except:
                messages.error(request, 'Ошибка при создании заказа')
            
            return redirect('create_order')

class CancelOrderView(View):
    def post(self, request, order_uuid):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.post(
            f'{API_BASE_URL}/client/{order_uuid}/cancel/',
            headers=headers
        )
        
        if response.status_code == 200:
            messages.success(request, 'Заказ успешно отменен')
        else:
            messages.error(request, 'Ошибка при отмене заказа')
            
        return redirect('profile')

class OrderHistoryView(View):
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.get(f'{API_BASE_URL}/client/order-history/', headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            context = {
                'orders': orders
            }
            return render(request, 'orders/order_history.html', context)
        else:
            messages.error(request, 'Ошибка при получении истории заказов')
            return redirect('profile') 
        
class RateStoreView(View):
    def post(self, request, order_uuid):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.post(
            f'{API_BASE_URL}/client/order/{order_uuid}/rate/',
            headers=headers,
            json={'rating': request.POST.get('rating')}
        )
        
        return redirect('order_history')    

class StoreOrderHistoryView(View):
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.get(f'{API_BASE_URL}/store/history/', headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            context = {
                'orders': orders
            }
            return render(request, 'orders/store_order_history.html', context)
        else:
            messages.error(request, 'Ошибка при получении истории заказов')
            return redirect('profile')    

class StoreOrdersView(View):
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.get(f'{API_BASE_URL}/store/orders/', headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            print("Orders received:", orders)  # Add logging
            context = {
                'orders': orders
            }
            
            # If it's an AJAX request, return only the orders list partial
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'orders/partials/orders_list.html', context)
                
            return render(request, 'orders/store_orders.html', context)
        else:
            messages.error(request, 'Ошибка при получении заказов')
            return redirect('profile')

class ProposePriceView(View):
    def post(self, request, order_id):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        data = {
            'proposed_price': request.POST.get('proposed_price'),
            'flower_img': request.FILES.get('flower_img'),
            'comment': request.POST.get('comment')
        }
        
        response = requests.post(
            f'{API_BASE_URL}/store/propose-price/{order_id}/',
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            messages.success(request, 'Цена успешно предложена')
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('detail', 'Ошибка при предложении цены')
                messages.error(request, error_message)
            except:
                messages.error(request, 'Ошибка при предложении цены')
        
        return redirect('store_orders')

class CurrentOrderView(View):
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.get(f'{API_BASE_URL}/me/', headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            context = {
                'user': user_data
            }
            return render(request, 'orders/current_order.html', context)
        else:
            messages.error(request, 'Ошибка при получении данных заказа')
            return redirect('profile')

class ClientProposedPricesView(View):
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.get(f'{API_BASE_URL}/client/proposed-prices/', headers=headers)
        
        if response.status_code == 200:
            prices = response.json()
            context = {
                'prices': prices
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'orders/partials/proposed_prices_list.html', context)
                
            return render(request, 'orders/proposed_prices.html', context)
        else:
            messages.error(request, 'Ошибка при получении предложений')
            return redirect('current_order')