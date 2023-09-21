from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_view, name='index'),
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('lessons/', views.LessonList.as_view(), name='lesson-list'),
    path('product-access/', views.ProductAccessList.as_view(), name='product-access-list'),
    path('lesson-views/', views.LessonViewList.as_view(), name='lesson-view-list'),

    # URL для задания
    path('user-lessons/', views.UserLessonListView.as_view(), name='user-lesson-list'),
    path('api/product-lessons/<int:product_id>/', views.ProductLessonListView.as_view(), name='product-lesson-list'),
    path('api/product-all/', views.ProductStatisticsView.as_view(), name='product-all'),
]