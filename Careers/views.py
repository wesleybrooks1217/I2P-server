from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import  Career
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import base64
import json
from django.http import HttpResponse, JsonResponse
from django.views import View
from courses import models as CoursesMod
import csv
from django.db.models import Q 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


# Create your views here.


class CareerViews(View):

    def call_onet(request, onet_id):
        headers = {
            'User-Agent': 'python-OnetWebService/1.00 (bot)',
            'Authorization': 'Basic ' + base64.standard_b64encode(("linkedin_company_myn" + ':' + "5725apz").encode()).decode(),
            'Accept': 'application/json' 
                        }
        
        url = "https://services.onetcenter.org/ws/mnm/careers/"

        req = urllib.request.Request(url, None, headers)
        handle = urllib.request.urlopen(req) 
        return JsonResponse(json.load(handle))

    def career_list(request):
        query = request.GET.get('q', '')
        median_salary = request.GET.get('Salary')
        industry = request.GET.get('Industries')
        education = request.GET.get('Education')

        careers = Career.objects.all()

        if query:
            careers = careers.filter(Q(career_name__icontains=query))
        if median_salary:
            careers = careers.filter(median_salary__gte=int(median_salary))
        if industry:
            careers = careers.filter(industry=industry)
        if education:
            careers = careers.filter(education=education)

        career_list = list(careers.values('id', 'career_name', 'onet_id'))
        mapped_data = []
        for career in career_list:
            mapped_data.append({
                "id": career.get("id"),
                "name": career.get("career_name"),
                "api_id": career.get("onet_id")
            })
        return JsonResponse({'list': mapped_data})

    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def liked_careers(request):
        user = request.user
        liked = user.likedCareers.all()
        career_list = list(liked.values('id', 'career_name', 'onet_id'))
        mapped_data = []
        for career in career_list:
            mapped_data.append({
                "id": career.get("id"),
                "name": career.get("career_name"),
                "api_id": career.get("onet_id")
            })
        return JsonResponse({'list': mapped_data})

    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def add_liked_career(request):
        user = request.user
        career_id = request.data.get('id')
        career = Career.objects.get(id=career_id)
        user.likedCareers.add(career)
        user.save()

        liked = user.likedCareers.all()
        career_list = list(liked.values('id', 'career_name', 'onet_id'))
        mapped_data = []
        for career in career_list:
            mapped_data.append({
                "id": career.get("id"),
                "name": career.get("career_name"),
                "api_id": career.get("onet_id")
            })
        return JsonResponse({'list': mapped_data})

    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def remove_liked_career(request):
        user = request.user
        career_id = request.data.get('id')
        user.likedCareers.filter(id=career_id).delete()

        liked = user.likedCareers.all()
        career_list = list(liked.values('id', 'career_name', 'onet_id'))
        mapped_data = []
        for career in career_list:
            mapped_data.append({
                "id": career.get("id"),
                "name": career.get("career_name"),
                "api_id": career.get("onet_id")
            })
        return JsonResponse({'list': mapped_data})

    def get_data_for_user_display(request, onet_id):
        headers = {
            'User-Agent': 'python-OnetWebService/1.00 (bot)',
            'Authorization': 'Basic ' + base64.standard_b64encode(("linkedin_company_myn" + ':' + "5725apz").encode()).decode(),
            'Accept': 'application/json' 
                        }
        
        url = "https://services.onetcenter.org/ws/mnm/careers/"+onet_id

        career_id = Career.objects.filter(onet_id=onet_id).values("id").first()
        if career_id:
            career_id = career_id["id"]

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.load(response)

            mapped_data = {
                "id": career_id,
                "name": data.get("title"),
                "description": data.get("what_they_do"),
                "api_id": data.get("code"),
                "attributes": data.get("on_the_job", {}).get("task", [])
            }
            return JsonResponse(mapped_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    
