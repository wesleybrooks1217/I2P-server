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

    # def get(self, request, *args, **kwargs):

    #     careers = Career.objects.all()
        
    #     search_query = request.GET.get('search', None)
    #     if search_query:
    #         careers = careers.filter(career_name_icontains=search_query)
        
    #     salary_query = request.GET.get('salary', None)
    #     if salary_query:
    #         careers = careers.filter(median_salary_gte=salary_query)

    #     education_query = request.GET.get('education', None)
    #     if education_query:
    #         careers = careers.filter(education=education_query)

    #     industry_query = request.GET.get('industry', None)
    #     if industry_query:
    #         careers = careers.filter(industry=industry_query)
        
    #     career_list = list(careers.values('id', 'career_name', 'onet_id', 'median_salary', 'industry', 'education'))

    #     return JsonResponse({'list': career_list})

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



    def career_serach(request, chars):
        
        careers = Career.objects.filter(career_name__startswith = chars)

        careers_list = []

        counter = 0
        for career in careers:

            if counter == 5:
                break

            careers_list.append({
                "career_name": career.career_name,
                "onet_id": career.onet_id
            })
            
            
            counter += 1

        return JsonResponse({"careers": careers_list})
    
        
    

    def career_filter(request):
        
        careers_business = Career.objects.filter(industry = "Business").values('career_name', 'onet_id')
        careers_agriculture = Career.objects.filter(industry = "Agriculture").values('career_name', 'onet_id')
        careers_manufacturing = Career.objects.filter(industry = "Manufacturing").values('career_name', 'onet_id')
        careers_health = Career.objects.filter(industry = "Health").values('career_name', 'onet_id')
        careers_engineering = Career.objects.filter(industry = "Engineering").values('career_name', 'onet_id')
        careers_human_resources = Career.objects.filter(industry = "Human Resources").values('career_name', 'onet_id')
        careers_30000 = Career.objects.filter(median_salary__gt = 30000).values('career_name', 'onet_id')
        careers_50000 = Career.objects.filter(median_salary__gt = 50000).values('career_name', 'onet_id')
        careers_75000 = Career.objects.filter(median_salary__gt = 75000).values('career_name', 'onet_id')
        careers_100000 = Career.objects.filter(median_salary__gt = 100000).values('career_name', 'onet_id')
        careers_125000 = Career.objects.filter(median_salary__gt = 125000).values('career_name', 'onet_id')
        careers_high_school = Career.objects.filter(education = "HighSchool").values('career_name', 'onet_id')
        careers_bachelors = Career.objects.filter(education = "Bachelors").values('career_name', 'onet_id')
        careers_masters = Career.objects.filter(education = "Masters").values('career_name', 'onet_id')
        careers_doctorate = Career.objects.filter(education = "Doctorate").values('career_name', 'onet_id')

        return JsonResponse({
            'business': list(careers_business),
            'agriculture': list(careers_agriculture),
            'manufacturing': list(careers_manufacturing),
            'health': list(careers_health),
            'engineering': list(careers_engineering),
            'human_resources': list(careers_human_resources),
            'thirty_thousand': list(careers_30000),
            'fifty_thousand': list(careers_50000),
            'seventyfive_thousand': list(careers_75000),
            'onehundred_thousand': list(careers_100000),
            'onehundredtwentyfive_thousand': list(careers_125000),
            'high_school': list(careers_high_school),
            'bachelors': list(careers_bachelors),
            'masters': list(careers_masters),
            'doctorate': list(careers_doctorate)
        })
    
    

    def career_filter_industry(request, industryIn):
        
        careers = Career.objects.filter(industry = industryIn).values('career_name', 'onet_id')
        return JsonResponse({'careers': list(careers)})
    

    def career_filter_salary(request, salaryIn):
        
        careers = Career.objects.filter(median_salary__gt = salaryIn).values('career_name', 'onet_id')

        return JsonResponse({'careers': list(careers)})

    def career_filter_education(request, education):

        careers = Career.objects.filter(education = education).values('career_name', 'onet_id')

        return JsonResponse({'careers': list(careers)})
    

    def load_careers(request):
    
    
    ##with codecs.open("Careers.xlsx", 'r', encoding='utf-8', errors='ignore') as f:
        
        with open("Careers.csv", 'rt') as f:
            reader = csv.reader(f)
            
            
            for row in reader:
                break

            counter = 0
            
            for row in reader:
                
                _, created = Career.objects.get_or_create(
                    career_name = row[0],
                    onet_id = row[1],
                    median_salary = int(row[2]),
                    industry = row[3],
                    education = row[4]
                )
        return HttpResponse({"Success"})
    
