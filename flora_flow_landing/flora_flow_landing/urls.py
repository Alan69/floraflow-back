from django.urls import path, include

urlpatterns = [
    # ... other URL patterns ...
    path('payments/', include('payments.urls', namespace='payments')),
] 