from django.shortcuts import render
from django.http import HttpResponse
from .logic import get_stock_data

# Create your views here.

def index(request):
    data = get_stock_data()
    print(data)
    return HttpResponse("hello world!")
