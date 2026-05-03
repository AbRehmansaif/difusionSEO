from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('services/advanced-seo-strategy/', views.seo_strategy, name='seo_strategy'),
    path('services/local-seo-services/', views.local_seo, name='local_seo'),
    path('services/full-stack-web-development/', views.web_development, name='web_development'),
    path('services/ai-automation-solutions/', views.ai_automation, name='ai_automation'),
    path('services/cyber-security-solutions/', views.cyber_security, name='cyber_security'),
    path('services/backlink-building-services/', views.backlink_service, name='backlink_service'),
    path('contact/', views.contact, name='contact'),
    path('leadnexus/', views.leadnexus, name='leadnexus'),
    path('privacy-policy/', views.privacy, name='privacy'),
    path('terms-of-service/', views.terms, name='terms'),
]
