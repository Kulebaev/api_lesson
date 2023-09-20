from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db.models import Count
from rest_framework.response import Response
from .models import Product, Lesson, ProductAccess, LessonView
from .serializers import ProductSerializer, LessonSerializer, ProductAccessSerializer, LessonViewSerializer
from rest_framework import generics


class ProductLessonListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Получить идентификатор продукта из параметров запроса
        product_id = self.kwargs.get('product_id')

        product_object = Product.objects.get(id=product_id)

        # Получить текущего пользователя
        user = self.request.user

        # Проверить, имеет ли пользователь доступ к этому продукту
        has_access = ProductAccess.objects.filter(user=user, product_id=product_object)

        # return has_access

        if not has_access.exists():
            # Если у пользователя нет доступа к продукту, вернуть пустой список
            return Lesson.objects.none()

        # Фильтровать уроки, связанные с данным продуктом
        queryset = Lesson.objects.filter(products=product_id)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        lesson_list = []

        for q in queryset:

            lesson_info = {
                'lesson_id': q.name,
                
            }

            lesson_list.append(lesson_info)

        return Response(lesson_list)


class UserLessonListView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # текущий пользователь
        user = self.request.user

        # Получить текущего пользователя
        user = self.request.user

        # Проверить, имеет ли пользователь доступ к этому продукту
        product_ids_with_access = ProductAccess.objects.filter(user=user)

        # return product_ids_with_access

        if not product_ids_with_access:
            # Если у пользователя нет доступа ни к одному продукту, вернуть пустой список
            return Lesson.objects.none()

        # Фильтровать уроки, связанные с продуктами, к которым у пользователя есть доступ
        queryset = Lesson.objects.filter(products__id__in=product_ids_with_access) \
                    .values('id') \
                    .annotate(lesson_count=Count('id'))

        return queryset


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        count = queryset.count()  # Получить количество элементов в queryset

        lesson_ids = queryset.values_list('id', flat=True)

        lesson_views = LessonView.objects.filter(lesson__id__in=lesson_ids)

        # return Response({'count': count, 'list': list(lesson_views)})

        # Список уроков
        lesson_list = []
        for lesson_data in lesson_views:
            lesson_name = lesson_data.first()
            viewing_time_seconds = lesson_data.viewing_time_seconds

            lesson_info = {
                'lesson_name': lesson_name.name,
                'viewing_time_seconds': viewing_time_seconds,
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

