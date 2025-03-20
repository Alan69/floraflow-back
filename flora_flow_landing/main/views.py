from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

TELEGRAM_BOT_TOKEN = '7878794010:AAE-E7zRnmO6xt06Gv8cuDLCkxOfUlmPZFQ'
TELEGRAM_CHAT_ID = '479612043'

def index(request):
    data = {
        'title': 'Главная',
    }
    return render(request, "main/index.html", data)

def privacy_policy(request):
    data = {
        'title': 'Политика конфиденциальности',
    }
    return render(request, "main/privacy_policy.html", data)

def contact(request):
    data = {
        'title': 'Связаться с нами',
    }
    return render(request, "main/contact.html", data)

@csrf_exempt
def send_support_message(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullName')
        contact_info = request.POST.get('contactInfo')
        message = request.POST.get('message')

        # Construct the message for Telegram
        telegram_message = f"📩 SUPPORT MESSAGE\n\n👤 ФИО: {full_name}\n📞 Контакт: {contact_info}\n\n💬 Сообщение:\n{message}"

        # Send the message to Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': telegram_message
        }
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            # Render a success page
            return render(request, 'main/success.html', {
                'message': 'Ваше сообщение успешно отправлено!',
                'details': 'Мы обработаем ваш запрос и свяжемся с вами в ближайшее время. Спасибо за обращение.'
            })
        else:
            # Render an error page
            return render(request, 'main/error.html', {
                'message': 'Ошибка при отправке сообщения.',
                'details': 'Пожалуйста, попробуйте снова позже или свяжитесь с нами по указанным контактам.'
            })

    # Render an error page for invalid request methods
    return render(request, 'main/error.html', {
        'message': 'Недопустимый метод запроса.',
        'details': 'Пожалуйста, используйте форму на нашем сайте для отправки сообщения.'
    })

@csrf_exempt
def send_to_telegram(request):
    if request.method == 'POST':
        name = request.POST.get('Name')
        phone = request.POST.get('Phone')
        using_type = request.POST.get('using_type')
        shop_name = request.POST.get('shop_name', '')  # Get shop_name, default to empty string if not provided

        # Construct the message
        message = f"👤 Имя: {name}\n📞 Телефон: {phone}\n📋 Использование: {using_type}"
        if using_type == 'shop' and shop_name:
            message += f"\n🏪 Название магазина: {shop_name}"

        # Send the message to Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            # Render a success page
            return render(request, 'main/success.html', {
                'message': 'Ваши данные успешно отправлены в Telegram!',
                'details': 'Мы свяжемся с вами в ближайшее время. Спасибо за использование нашего сервиса.'
            })
        else:
            # Render an error page
            return render(request, 'main/error.html', {
                'message': 'Ошибка при отправке данных в Telegram.',
                'details': 'Пожалуйста, проверьте данные и попробуйте снова позже.'
            })

    # Render an error page for invalid request methods
    return render(request, 'main/error.html', {
        'message': 'Недопустимый метод запроса.',
        'details': 'Пожалуйста, отправьте данные через форму на нашем сайте.'
    })
