from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from django.db.models import Case, When, Value, BooleanField, IntegerField, F
from rest_framework.response import Response
from .models import Product, Lesson, ProductAccess, LessonView
from .serializers import ProductSerializer, LessonSerializer, ProductAccessSerializer, LessonViewSerializer
from rest_framework import generics, serializers


class LessonSerializer(serializers.Serializer):
    name=serializers.CharField()
    total_viewing_time=serializers.IntegerField()
    status=serializers.CharField()
    duration_seconds=serializers.IntegerField()


class UserLessonListView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=LessonSerializer

    def get_queryset(self):
        # текущий пользователь
        user=self.request.user

        product_access=ProductAccess.objects.filter(user=user).values('product')
        
        lesson_with_view=Lesson.objects.filter(
            products__in=product_access).annotate(
                total_viewing_time=Case(
                    When(
                        lessonview__user=user, then=F('lessonview__viewing_time_seconds')
                        ), default=Value(0), output_field=IntegerField()
                )
            )

        lesson_with_view = lesson_with_view.annotate(
                    percent=Case(
                        When(total_viewing_time__gt=0,
                             duration_seconds__gt=0,
                             then=F('total_viewing_time') * 100 / F('duration_seconds'),
                    ),default=Value(0),output_field=IntegerField()),
                     status=Case(
                        When(percent__gte=80,
                             then=Value('Просмотренно'),
                    ),default=Value('Не просмотренно')),
                    )

        return lesson_with_view


    def list(self, request, *args, **kwargs):
        queryset=self.filter_queryset(self.get_queryset())

        unique_lessons=queryset.distinct() # Только уникальные поля
        
        serialized_data = self.serializer_class(unique_lessons, many=True).data

        return Response(serialized_data)
        # Список уроков
        lesson_list = []
        for lesson_data in unique_lessons:

            # Рассчитать процент
            if lesson_data.duration_seconds > 0:
                viewing_percentage = (lesson_data.total_viewing_time / lesson_data.duration_seconds) * 100
            else:
                viewing_percentage = 0

            lesson_info = {'lesson_name': lesson_data.name,
                        'status': 'Просмотрено' if viewing_percentage >= 80 else 'Не просмотрено',
                        'viewing_time': lesson_data.total_viewing_time,
                    }
            
            lesson_list.append(lesson_info)
        
        
        return Response(lesson_list)  # данные в формате json


class ProductLessonListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Получить идентификатор продукта из параметров запроса
        product_id=self.kwargs.get('product_id')
        product_object=Product.objects.filter(id=product_id)
        # Получить текущего пользователя
        user = self.request.user

        # Фильтровать уроки, связанные с данным продуктом и пользователем
        lesson_with_view=Lesson.objects.filter(
            products__in=product_object).annotate(
                timestamp=Case(
                    When(lessonview__user=user, 
                         then=F('lessonview__timestamp')), default=None),
                total_viewing_time=Case(
                    When(lessonview__user=user, 
                         then=F('lessonview__viewing_time_seconds')), default=Value(0), output_field=IntegerField()
                )
            )

        return lesson_with_view
    

    def list(self, request, *args, **kwargs):
        queryset=self.filter_queryset(self.get_queryset())

        unique_lessons=queryset.distinct() # Только уникальные поля
        
        product_list=[]

        for lesson in unique_lessons:

            # Проверить, был ли просмотр и получить дату последнего просмотра
            last_viewed_date = None
            
            if lesson.timestamp is not None:
                last_viewed_date = lesson.timestamp.strftime("%Y-%m-%d")


            product_info = {
                'lesson_name': lesson.name,
                'viewing_time': lesson.total_viewing_time,
                'last_viewed_date': last_viewed_date
            }

            product_list.append(product_info)

        return Response(product_list)








class ProductList(generics.ListCreateAPIView):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer

class LessonList(generics.ListCreateAPIView):
    queryset=Lesson.objects.all()
    serializer_class=LessonSerializer

class ProductAccessList(generics.ListCreateAPIView):
    queryset=ProductAccess.objects.all()
    serializer_class=ProductAccessSerializer

class LessonViewList(generics.ListCreateAPIView):
    queryset = LessonView.objects.all()
    serializer_class = LessonViewSerializer


def index_view(request):
    current_user=request.user
    # Теперь переменная current_user содержит информацию о текущем пользователе
    return render(request, 'index.html', {'current_user': current_user})

