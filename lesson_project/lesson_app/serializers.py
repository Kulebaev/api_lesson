from rest_framework import serializers
from .models import Product, Lesson, ProductAccess, LessonView

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class ProductAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAccess
        fields = '__all__'

class LessonViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonView
        fields = '__all__'
