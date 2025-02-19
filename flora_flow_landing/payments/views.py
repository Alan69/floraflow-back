from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
import requests
from django.conf import settings

API_BASE_URL = settings.BASE_URL + '/api'

class TariffsView(View):
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.get(f'{API_BASE_URL}/tariffs/', headers=headers)
        
        if response.status_code == 200:
            tariffs = response.json()
            return render(request, 'payments/tariffs.html', {'tariffs': tariffs})
        else:
            messages.error(request, 'Ошибка при получении тарифов')
            return redirect('profile')

class InitiatePaymentView(View):
    def post(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        tariff_uuid = request.POST.get('tariff_uuid')
        
        # First, get payment token
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        token_response = requests.post(f'{API_BASE_URL}/payment/token/', headers=headers)
        
        if token_response.status_code != 200:
            messages.error(request, 'Ошибка при инициализации платежа')
            return redirect('tariffs')
            
        token = token_response.json().get('access_token')
        
        # Initiate payment
        payment_data = {
            'token': token,
            'tariff_uuid': tariff_uuid
        }
        
        payment_response = requests.post(
            f'{API_BASE_URL}/payment/initiate/',
            headers=headers,
            json=payment_data
        )
        
        if payment_response.status_code == 200:
            payment_data = payment_response.json()
            return redirect(payment_data['invoice_url'])
        else:
            messages.error(request, 'Ошибка при создании платежа')
            return redirect('tariffs')

class CheckPaymentStatusView(View):
    def get(self, request):
        if not request.session.get('access_token'):
            return redirect('login')
            
        headers = {'Authorization': f'Bearer {request.session["access_token"]}'}
        response = requests.post(f'{API_BASE_URL}/payment/status/', headers=headers)
        
        if response.status_code == 200:
            messages.success(request, 'Оплата успешно произведена')
        else:
            messages.error(request, 'Оплата не прошла или находится в обработке')
            
        return redirect('profile') 