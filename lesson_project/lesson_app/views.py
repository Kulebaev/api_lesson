from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from django.db.models import Case, When, Value, IntegerField, F, Sum, Count, FloatField, ExpressionWrapper
from django.contrib.auth.models import User
from django.db.models.functions import TruncDate, Coalesce
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
                        ), default=Value(0), output_field=IntegerField()),
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


class ProductLessonSerializer(serializers.Serializer):
    name=serializers.CharField()
    total_viewing_time=serializers.IntegerField()
    timestamp_formatted=serializers.CharField()


class ProductLessonListView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=ProductLessonSerializer

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
                ),
                timestamp_formatted=TruncDate(
                    F('lessonview__timestamp'),  # Форматируем дату
                    )
            )

        return lesson_with_view
    

    def list(self, request, *args, **kwargs):
        queryset=self.filter_queryset(self.get_queryset())

        unique_lessons=queryset.distinct() # Только уникальные поля

        serialized_data = self.serializer_class(unique_lessons, many=True).data

        return Response(serialized_data)
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


class ProductAllSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    name=serializers.CharField()
    lesson_views=serializers.IntegerField()
    total_viewing_time=serializers.IntegerField()
    num_students=serializers.IntegerField()
    purchase_percentage=serializers.IntegerField()


class ProductStatisticsView(generics.ListAPIView):
    serializer_class=ProductAllSerializer

    def get_queryset(self):
        products = Product.objects.all()
        total_users = User.objects.count()

        products = Product.objects.annotate(
            lesson_views=Count('lesson__lessonview', filter=F('lesson__lessonview__viewed')),
            total_viewing_time=Coalesce(Sum('lesson__lessonview__viewing_time_seconds'), 0),
            num_students=Count('productaccess__user', distinct=True),
            total_users=Value(total_users)
        ).annotate(
            purchase_percentage=ExpressionWrapper(
                (Count('productaccess__user', distinct=True) * 100 / F('total_users')) ,
                output_field=FloatField()
            )
        )

        return products


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serialized_data = self.serializer_class(queryset, many=True).data

        return Response(serialized_data)

        serialized_data = [
            {
                'product_id': product.id,
                'product_name': product.name,
                'lesson_views': product.lesson_views,
                'total_viewing_time_seconds': product.total_viewing_time,
                'num_students': product.num_students,
                'purchase_percentage': product.purchase_percentage,
            }
            for product in queryset
        ]

        return Response(serialized_data)






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

