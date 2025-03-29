from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import  College
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

class CollegeView(View):

    def college_list(request):
        query = request.GET.get('q', '')
        accpetance_rate = request.GET.get('AcceptanceRate')
        financial_aid = request.GET.get('Financial Aid')
        sat_score = request.GET.get("SAT Score")
        yearly_earnings = request.GET.get("Yearly Earnings")

        colleges = College.objects.all()
        if query:
            colleges = colleges.filter(Q(name__icontains=query))
        if accpetance_rate:
            colleges = colleges.filter(acceptance_rate__gte=int(accpetance_rate))
        if financial_aid:
            colleges = colleges.filter(average_fin_aid__gte=int(financial_aid))
        if sat_score:
            colleges = colleges.filter(sat_score__gte=int(sat_score))
        if yearly_earnings:
            colleges = colleges.filter(yearly_earnings__gte=int(yearly_earnings))
        
        college_list = list(colleges.values('id', 'name'))
        mapped_data = []
        for college in college_list:
            mapped_data.append({
                "id": college.get("id"),
                "name": college.get("name"),
                "api_id": college.get("id")
            })
        
        return JsonResponse({'list': mapped_data})

    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def liked_colleges(request):
        user = request.user
        liked = user.likedSchools.all()
        college_list = list(liked.values('id', 'name'))
        mapped_data = []
        for college in college_list:
            mapped_data.append({
                "id": college.get("id"),
                "name": college.get("name"),
                "api_id": college.get("id")
            })

        return JsonResponse({'list': mapped_data})

    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def add_liked_college(request):
        user = request.user
        college_id = request.data.get('id')
        college = College.objects.get(id=college_id)
        user.likedSchools.add(college)
        user.save()

        liked = user.likedSchools.all()
        college_list = list(liked.values('id', 'name'))
        mapped_data = []
        for college in college_list:
            mapped_data.append({
                "id": college.get("id"),
                "name": college.get("name"),
                "api_id": college.get("id")
            })

        return JsonResponse({'list': mapped_data})

    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def remove_liked_college(request):
        user = request.user
        college_id = request.data.get('id')
        user.likedSchools.filter(id=college_id).delete()

        liked = user.likedSchools.all()
        college_list = list(liked.values('id', 'name'))
        mapped_data = []
        for college in college_list:
            mapped_data.append({
                "id": college.get("id"),
                "name": college.get("name"),
                "api_id": college.get("id")
            })

        return JsonResponse({'list': mapped_data})

    def get_data_for_user_display(request, id):
        college = College.objects.get(id=id)
        name = college.name
        acceptance_rate = college.acceptance_rate
        description = f"{name} has an acceptance rate of {acceptance_rate} percent"
        fin_aid = f"Average financial aid: {college.average_fin_aid}"
        sat_score = f"Average SAT score: {college.sat_score}"
        yearly_earnings = f"Average graduate yearly earnings: {college.yearly_earnings}"
        attributes = [fin_aid, sat_score, yearly_earnings]
        mapped_data = {
            "id": id,
            "name": name,
            "description": description,
            "api_id": id,
            "attributes": attributes
        }
        return JsonResponse(mapped_data)

