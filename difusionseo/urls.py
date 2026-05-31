"""
URL configuration for difusionseo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from core import views as core_views

# Admin branding
admin.site.site_header = "DifusionSEO Administration"
admin.site.site_title = "DifusionSEO Admin"
admin.site.index_title = "Welcome to DifusionSEO Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('googlebc81c2a12a2d31f1.html', TemplateView.as_view(template_name="googlebc81c2a12a2d31f1.html", content_type="text/html")),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', core_views.sitemap_view, name='sitemap'),
    path('blogs/', include('blogs.urls', namespace='blogs')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('core.urls')),
]

from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Force serve media in production since users usually forget to configure web servers initially.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
