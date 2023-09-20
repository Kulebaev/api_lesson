from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from django.db import models
from rest_framework.response import Response
from .models import Product, Lesson, ProductAccess, LessonView
from .serializers import ProductSerializer, LessonSerializer, ProductAccessSerializer, LessonViewSerializer
from rest_framework import generics


class UserLessonListView(generics.ListAPIView):
    serializer_class = LessonViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # текущий пользователь
        user = self.request.user

        product_access = ProductAccess.objects.filter(user=user).values('product')

        lesson = Lesson.objects.filter(products__in=product_access)

        return LessonView.objects.filter(lesson__in=lesson).select_related("lesson")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        unique_lessons = queryset.values('lesson').distinct()

        # Список уроков
        lesson_list = []
        for lesson_data in unique_lessons:
            lesson_id = lesson_data['lesson']
            lesson_views = queryset.filter(lesson=lesson_id)
            total_duration_seconds = lesson_views.first().lesson.duration_seconds
            
            lesson_view = lesson_views.first()
    
            # Проверяем, что lesson_view не равен None
            if lesson_view:
                total_viewing_time = lesson_view.viewing_time_seconds
            else:
                total_viewing_time = 0  # Устанавливаем значение по умолчанию, если lesson_view равен None

            # Рассчитать процент
            if total_duration_seconds > 0:
                viewing_percentage = (total_viewing_time / total_duration_seconds) * 100
            else:
                viewing_percentage = 0

            lesson_info = {
                'lesson_id': lesson_id,
                'lesson_name': lesson_view.lesson.name,
                'status': 'Просмотрено' if viewing_percentage >= 80 else 'Не просмотрено'
    }

            lesson_list.append(lesson_info)

        return Response(lesson_list)  # данные в формате json


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class LessonList(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class ProductAccessList(generics.ListCreateAPIView):
    queryset = ProductAccess.objects.all()
    serializer_class = ProductAccessSerializer

class LessonViewList(generics.ListCreateAPIView):
    queryset = LessonView.objects.all()
    serializer_class = LessonViewSerializer


def index_view(request):
    current_user = request.user
    # Теперь переменная current_user содержит информацию о текущем пользователе
    return render(request, 'index.html', {'current_user': current_user})

