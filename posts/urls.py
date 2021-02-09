from django.urls import path

from . import views

urlpatterns = [

    path('', views.index, name='index'),
    # новая запись
    path('new/', views.new_post, name='new'),
    # Профайл пользователя
    path('<str:username>/', views.profile, name='profile'),
    # Просмотр записи
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    # редактирование записи
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit,
         name='post_edit'),

    path("<username>/<int:post_id>/comment", views.add_comment,
         name="add_comment"),

    # страница группы
    path('group/<slug:slug>/', views.group_posts, name='group'),

]
