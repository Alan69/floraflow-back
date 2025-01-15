from django.shortcuts import render


def index(request):
    data = {
        'title': 'Главная',
    }
    return render(request, "landing/index.html", data)
