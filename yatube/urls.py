from django.conf import settings
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

from posts.views import page_not_found, server_error

urlpatterns = [

    path('about/', include('django.contrib.flatpages.urls')),
    # path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about_us'),
    # path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
    path('about/author/', views.flatpage, {'url': 'about/author/'},
         name='about/author'),
    path('/about/tech/', views.flatpage, {'url': 'about/tech/'},
         name='about-spec'),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
    path('', include('posts.urls')),
    path('404/', page_not_found, name='404'),
    path('500/', server_error, name='500')]

handler404 = "posts.views.page_not_found"  # noqa
handler500 = "posts.views.server_error"  # noqa

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
