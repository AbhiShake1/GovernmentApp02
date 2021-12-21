from django.http import HttpResponse, HttpRequest

# Create your views here.
from core import document_util


def home(request):
    return HttpResponse("Status: Running")


def pdf(request: HttpRequest, base64_string: int):
    return HttpResponse(base64_string)
