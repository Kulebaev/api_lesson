import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lesson_project.settings')

# настройки Django
django.setup()

# модели
from django.contrib.auth.models import User
from lesson_app.models import Product, Lesson, ProductAccess, LessonView

# код для создания и сохранения данных в базе данных
def add_data():
    user = User.objects.create(username='example_user', password='1')

    product1 = Product.objects.create(owner=user, name='Product 1')
    product2 = Product.objects.create(owner=user, name='Product 2')

    lesson1 = Lesson.objects.create(name='Lesson 1', video_link='https://example.com/lesson1', duration_seconds=600)
    lesson2 = Lesson.objects.create(name='Lesson 2', video_link='https://example.com/lesson2', duration_seconds=900)

    lesson1.products.add(product1)
    lesson2.products.add(product1, product2)

    product_access1 = ProductAccess.objects.create(user=user, product=product1)
    product_access2 = ProductAccess.objects.create(user=user, product=product2)

    lesson_view1 = LessonView.objects.create(user=user, lesson=lesson1, viewed=True, viewing_time_seconds=600)
    lesson_view2 = LessonView.objects.create(user=user, lesson=lesson2, viewed=False, viewing_time_seconds=0)

    print('Данные успешно добавлены в базу данных.')

if __name__ == '__main__':
    add_data()
