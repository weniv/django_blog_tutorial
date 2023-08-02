from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
# rest_framework 추가 후 추가된 코드
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view


def index(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')

# FBV에서 사용하는 방식
@api_view(['GET'])
def test(request):
    data = [
        {'name': 'leehojun', 'age':10},
        {'name': 'leehojun2', 'age':20}
    ]
    return Response('hello world') # 1. 문자열로 응답
    # return Response(data) # 2. json으로 응답

# CBV에서 사용하는 방식
# class TestView(APIView):
#     def get(self, request):
#         data = [
#             {'name': 'leehojun', 'age':10},
#             {'name': 'leehojun2', 'age':20}
#         ]
#         return Response(data)
# test = TestView.as_view()

