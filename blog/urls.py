from django.urls import path
from . import views

urlpatterns = [
    path('', views.postlist, name='postlist'),
    path('<int:pk>/', views.postdetail, name='postdetail'),
    path('write/', views.write, name='postwrite'),
    path('edit/<int:pk>', views.edit, name='postedit'),
    path('delete/<int:pk>', views.delete, name='postdelete'),
    path('<int:pk>/new_comment/', views.new_comment, name='new_comment'),
    path('update_comment/<int:pk>/', views.update_comment, name='update_comment'),
    path('delete_comment/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('category/<str:slug>/', views.category_page, name='category_page'),
    path('tag/<str:slug>/', views.tag_page, name='tag_page'),
]