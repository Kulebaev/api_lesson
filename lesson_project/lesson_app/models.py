from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

class Lesson(models.Model):
    name = models.CharField(max_length=255)
    video_link = models.URLField()
    duration_seconds = models.IntegerField()
    products = models.ManyToManyField(Product)

class ProductAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class LessonView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    viewed = models.BooleanField(default=False)
    viewing_time_seconds = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

