from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import  Courses
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

class CoursesView(View):
    
    def course_list(request):
        query = request.GET.get('q', '')
        ap = request.GET.get('AP')
        de = request.GET.get('Duel Enrollment')
        honors = request.GET.get("Honors")
        difficulty = request.GET.get("Difficulty")

        courses = Courses.objects.all()
        if query:
            courses = courses.filter(Q(name__icontains=query))
        if ap:
            print(ap)
            courses = courses.filter(ap=(1 if ap == "AP" else 0))
        if de:
            courses = courses.filter(duelEnrollment=(1 if de == "Duel Enrollment" else 0))
        if honors:
            courses = courses.filter(honors=(1 if honors == "Honors" else 0))
        if difficulty:
            courses = courses.filter(difficulty=int(difficulty))
        
        course_list = list(courses.values('id', 'name'))
        mapped_data = []
        for course in course_list:
            mapped_data.append({
                "id": course.get("id"),
                "name": course.get("name"),
                "api_id": course.get("id")
            })
        
        return JsonResponse({'list': mapped_data})

    @api_view(['GET'])
    @permission_classes([IsAuthenticated])
    def liked_course(request):
        user = request.user
        liked = user.likedCourses.all()
        course_list = list(liked.values('id', 'name'))
        mapped_data = []
        for course in course_list:
            mapped_data.append({
                "id": course.get("id"),
                "name": course.get("name"),
                "api_id": course.get("id")
            })

        return JsonResponse({'list': mapped_data})

    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def add_liked_course(request):
        user = request.user
        course_id = request.data.get('id')
        course = Courses.objects.get(id=course_id)
        user.likedCourses.add(course)
        user.save()

        liked = user.likedCourses.all()
        course_list = list(liked.values('id', 'name'))
        mapped_data = []
        for course in course_list:
            mapped_data.append({
                "id": course.get("id"),
                "name": course.get("name"),
                "api_id": course.get("id")
            })

        return JsonResponse({'list': mapped_data})

    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def remove_liked_course(request):
        user = request.user
        course_id = request.data.get('id')
        user.likedCourses.filter(id=course_id).delete()

        liked = user.likedCourses.all()
        course_list = list(liked.values('id', 'name'))
        mapped_data = []
        for course in course_list:
            mapped_data.append({
                "id": course.get("id"),
                "name": course.get("name"),
                "api_id": course.get("id")
            })

        return JsonResponse({'list': mapped_data})

    def get_data_for_user_display(request, id):
        course = Courses.objects.get(id=id)
        name = course.name
        description = course.description
        ap = f"Is the course Advanced Placement? : {course.ap}"
        de = f"Is the course Duel Enrollment? : {course.duelEnrollment}"
        honors = f"Is the course Honors? : {course.honors}"
        difficulty = f"Relative Course Difficulty: {course.difficulty}"
        attributes = [ap, de, honors, difficulty]
        mapped_data = {
            "id": id,
            "name": name,
            "description": description,
            "api_id": id,
            "attributes": attributes
        }
        return JsonResponse(mapped_data)
