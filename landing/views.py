from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

TELEGRAM_BOT_TOKEN = '7878794010:AAE-E7zRnmO6xt06Gv8cuDLCkxOfUlmPZFQ'
TELEGRAM_CHAT_ID = '1614330612'

def index(request):
    data = {
        'title': 'Главная',
    }
    return render(request, "landing/index.html", data)

@csrf_exempt
def send_to_telegram(request):
    if request.method == 'POST':
        name = request.POST.get('Name')
        phone = request.POST.get('Phone')
        using_type = request.POST.get('using_type')

        # Construct the message
        message = f"👤 Имя: {name}\n📞 Телефон: {phone}\n📋 Использование: {using_type}"

        # Send the message to Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            return JsonResponse({'status': 'success', 'message': 'Data sent to Telegram successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to send data to Telegram.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
