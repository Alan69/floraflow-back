from datetime import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Tariff
from .serializers import TariffSerializer
import requests
from django.conf import settings
from rest_framework import status
import json
from users.models import CustomUser
from .utils import generate_secret_hash

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tariffs(request):
    """
    API view to retrieve all available tariff plans.
    """
    tariffs = Tariff.objects.all()
    serializer = TariffSerializer(tariffs, many=True)
    return Response(serializer.data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_payment_token(request):
    """
    View to retrieve the payment token from Halyk Bank.
    """
    url = 'https://epay-oauth.homebank.kz/oauth2/token'
    data = {
        'grant_type': 'password',
        'username': 'avirbox@mail.ru',
        'password': 'bynbo5-Wodjis-rebdor',
        'scope': 'webapi usermanagement email_send verification statement statistics payment', 
        'client_id': settings.HALYK_CLIENT_ID,
        'client_secret': settings.HALYK_CLIENT_SECRET,
        # 'secret_hash': generate_secret_hash(), 
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return Response(response.json(), status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to get payment token", "details": response.json()}, status=response.status_code)

@swagger_auto_schema(
    method='post',
    operation_description="Initiate a payment for the selected tariff using Halyk Bank Invoice Link API.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description="Token."),
            'tariff_uuid': openapi.Schema(type=openapi.TYPE_STRING, description="tariff uuid."),
        },
        required=['token', 'tariff_uuid']
    ),
    responses={
        200: openapi.Response(
            'Payment initiated successfully', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'payment_url': openapi.Schema(type=openapi.TYPE_STRING, description="URL to complete the payment."),
                    'invoice_id': openapi.Schema(type=openapi.TYPE_STRING, description="Unique invoice ID for the payment.")
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    View to initiate the payment for the selected tariff.
    """
    user = request.user
    tariff_uuid = request.data.get('tariff_uuid')
    tariff = Tariff.objects.get(uuid=tariff_uuid)
    
    # Get the payment token
    token = request.data.get('token')
    if not token:
        return Response({"error": "Payment token is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Generate a unique invoice ID (ensure uniqueness)
    invoice_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
    account_id = f"{user.uuid}"

    invoice_id = ''.join(char for char in invoice_id if char.isdigit())
    
    user.invoice_id = invoice_id
    user.save()

    # Prepare payment data according to the Halyk Bank Invoice Link API
    payment_data = {
        'shop_id': '761429bf-a56a-4871-8a14-c5be5f0296e5',
        'account_id': account_id,
        'invoice_id': invoice_id,
        'amount': int(tariff.price),
        'language': 'rus',
        'description': tariff.name,
        'expire_period': '1d',
        'recipient_contact': user.email,
        # 'recipient_contact_sms': user.phone,
        'recipient_contact_sms': '+77085731059',
        'notifier_contact_sms': '',
        'currency': 'KZT',
        'post_link': '',
        'failure_post_link': '',
        'back_link': 'https://www.google.com/',
        'failure_back_link': 'https://www.google.com/'
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Step 3: Send the request to Halyk Bank's payment API
    response = requests.post('https://epay-api.homebank.kz/invoice', data=json.dumps(payment_data), headers=headers)

    # Debugging: Log the raw response content and status code
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.text)

    if response.status_code == 200:
        try:
            response_data = response.json()
            payment_url = response_data.get('invoice_url')
            return Response({
                "invoice_url": payment_url,
                "invoice_id": invoice_id
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            # Handle JSON decode error
            return Response({"error": "Invalid JSON response from payment gateway", "details": response.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # Handle non-200 responses
        try:
            error_details = response.json()
        except ValueError:
            error_details = response.text  # Fallback to raw text if JSON parsing fails
        return Response({"error": f"Payment initiation failed", "details": error_details,}, status=response.status_code)

@swagger_auto_schema(
    method='post',
    operation_description="Check the status of a payment link for the current user. The request will return the status of the payment if the invoice is valid.",
    responses={
        200: openapi.Response(
            description="Payment status retrieved successfully",
            examples={
                "application/json": {
                    "message": "Оплата прошла успешно",
                    "status": {
                        "TotalCount": 1,
                        "Records": [{
                            "id": "7866f89b-6501-4515-9ba7-6e730443b22f",
                            "shop_id": "761429bf-a56a-4871-8a14-c5be5f0296e5",
                            "amount": 1500,
                            "invoice_id": "20250205101749",
                            "invoice_alt": "",
                            "language": "rus",
                            "currency": "KZT",
                            "description": "Дневной",
                            "account_id": "",
                            "recipient_contact": "test1234@mail.com",
                            "recipient_contact_sms": "+77085731059",
                            "notifier_contact": "",
                            "notifier_contact_sms": "+77085731059",
                            "expire_period": "1d",
                            "post_link": "",
                            "failure_post_link": "",
                            "back_link": "",
                            "failure_back_link": "",
                            "created_date": "2025-02-05T15:17:49.436355+05:00",
                            "expire_date": "2025-02-06T15:17:49.436355+05:00",
                            "status": "ACTIVE",
                            "updated_date": "0001-01-01T05:07:48+05:07",
                            "invoice_url": "https://epay-api.homebank.kz/redirect/invoice-link/7866f89b-6501-4515-9ba7-6e730443b22f",
                            "merchant_id": "52425b15-f354-4128-8cb9-de76f2ea614e",
                            "terminal_id": "2c9b7ad4-c02d-4898-8d00-3295497bbe53",
                            "card_save": False,
                            "data": ""
                        }]
                    }
                }
            }
        ),
        400: openapi.Response(
            description="Payment not successful or invalid request",
            examples={
                "application/json": {
                    "error": "Оплата не прошла",
                    "status": {
                        "TotalCount": 1,
                        "Records": [{
                            "id": "7866f89b-6501-4515-9ba7-6e730443b22f",
                            "shop_id": "761429bf-a56a-4871-8a14-c5be5f0296e5",
                            "amount": 1500,
                            "invoice_id": "20250205101749",
                            "invoice_alt": "",
                            "language": "rus",
                            "currency": "KZT",
                            "description": "Дневной",
                            "account_id": "",
                            "recipient_contact": "test1234@mail.com",
                            "recipient_contact_sms": "+77085731059",
                            "notifier_contact": "",
                            "notifier_contact_sms": "+77085731059",
                            "expire_period": "1d",
                            "post_link": "",
                            "failure_post_link": "",
                            "back_link": "",
                            "failure_back_link": "",
                            "created_date": "2025-02-05T15:17:49.436355+05:00",
                            "expire_date": "2025-02-06T15:17:49.436355+05:00",
                            "status": "ACTIVE",
                            "updated_date": "0001-01-01T05:07:48+05:07",
                            "invoice_url": "https://epay-api.homebank.kz/redirect/invoice-link/7866f89b-6501-4515-9ba7-6e730443b22f",
                            "merchant_id": "52425b15-f354-4128-8cb9-de76f2ea614e",
                            "terminal_id": "2c9b7ad4-c02d-4898-8d00-3295497bbe53",
                            "card_save": False,
                            "data": ""
                        }]
                    }
                }
            }
        ),
        404: openapi.Response(
            description="Invoice not found",
            examples={
                "application/json": {
                    "error": "No records found for the provided Invoice ID."
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_payment_status(request):
    """
    View to check the payment status for the provided Invoice ID and update the user's tariff if the payment is successful.
    """
    
    user = request.user
    invoice_id = user.invoice_id

    if not invoice_id:
        return Response({"error": "Invoice ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Step 1: Get OAuth Token
    oauth_url = 'https://epay-oauth.homebank.kz/oauth2/token'
    oauth_data = {
        'grant_type': 'password',
        'username': 'avirbox@mail.ru',
        'password': 'bynbo5-Wodjis-rebdor',
        'scope': 'webapi usermanagement email_send verification statement statistics payment',
        'client_id': settings.HALYK_CLIENT_ID,
        'client_secret': settings.HALYK_CLIENT_SECRET
    }

    oauth_response = requests.post(oauth_url, data=oauth_data)
    
    if oauth_response.status_code != 200:
        return Response({"error": "Failed to get access token", "details": oauth_response.json()}, status=status.HTTP_400_BAD_REQUEST)

    access_token = oauth_response.json().get('access_token')
    
    # Step 2: Check Payment Status using the access token
    url = 'https://epay-api.homebank.kz/invoice-links'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    data = {
        "paging": {
            "skip": 0,
            "limit": 1
        },
        "searchParameters": [
            {
                "name": "invoice_id",
                "method": "=",
                "searchParameter": [
                    invoice_id
                ]
            }
        ],
        "orderParameters": {
            "field": "id",
            "typeOrder": "DESC"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        if response_data['TotalCount'] > 0:
            payment_status = response_data['Records'][0].get("status")
            # If payment status is "CHARGED", update user's tariff
            if payment_status == "CHARGED":
                try:
                    # Find the user by account ID
                    user = CustomUser.objects.get(uuid=user.uuid)
                except CustomUser.DoesNotExist:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
                
                description = response_data['Records'][0].get("description")
                try:
                    tariff = Tariff.objects.get(name=description)
                except Tariff.DoesNotExist:
                    return Response({"error": "Tariff not found"}, status=status.HTTP_404_NOT_FOUND)

                user.tariff = tariff
                user.save()
                return Response({"message": "Оплата прошла успешно", "status": response_data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Оплата не прошла", "status": response_data}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "No records found for the provided Invoice ID."}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        "error": "Failed to retrieve payment status",
        "details": response.json()
    }, status=response.status_code)