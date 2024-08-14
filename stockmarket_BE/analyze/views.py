from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .finance_api_logic import call_api
from .financial_logic import *

# Create your views here.
def index(request):

    ticker = 'JPM'
    price_data, options_call_data, options_put_data = call_api(ticker)
    price_data = add_columns_stock_data(price_data)
    options_call_data = add_columns_option_data(options_call_data, price_data, type='call')
    options_put_data = add_columns_option_data(options_put_data, price_data, type='put')

    data = {
        'price_data': price_data.to_dict(orient='records'),
        'options_call_data': options_call_data[1].to_dict(orient='records'),
        'options_put_data': options_put_data[1].to_dict(orient='records')
    }

    return JsonResponse(data)

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]