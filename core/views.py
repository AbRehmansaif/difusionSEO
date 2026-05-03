from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactSubmission


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def seo_strategy(request):
    return render(request, 'services/seo_strategy.html')

def local_seo(request):
    return render(request, 'services/local_seo.html')

def web_development(request):
    return render(request, 'services/web_development.html')

def ai_automation(request):
    return render(request, 'services/ai_automation.html')

def cyber_security(request):
    return render(request, 'services/cyber_security.html')

def backlink_service(request):
    return render(request, 'services/backlinks.html')

def contact(request):
    if request.method == 'POST':
        # Honeypot check — bots fill this hidden field
        if request.POST.get('bot_check'):
            return redirect('contact')

        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        phone   = request.POST.get('phone', '').strip()
        service = request.POST.get('service', '').strip()
        message = request.POST.get('message', '').strip()

        # Basic server-side validation
        if len(name) >= 3 and email and service and len(message) >= 20:
            ContactSubmission.objects.create(
                name=name,
                email=email,
                phone=phone,
                service=service,
                message=message,
            )
            messages.success(request, 'success')
        else:
            messages.error(request, 'Please fill in all required fields correctly.')

        return redirect('contact')

    return render(request, 'contact.html')

def leadnexus(request):
    return render(request, 'leadnexus.html')

def privacy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')

def location_page(request, country_slug):
    valid_countries = ['italy', 'spain', 'germany', 'netherlands', 'uk', 'usa', 'canada', 'australia', 'new-zealand', 'france', 'switzerland']
    if country_slug.lower() in valid_countries:
        return render(request, f'locations/{country_slug.lower()}.html')
    from django.http import Http404
    raise Http404("Location not found")
