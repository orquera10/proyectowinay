from django.urls import path

from .views import contact_submit, home, info_page, post_detail

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('contacto/', contact_submit, name='contact_submit'),
    path('mision-y-vision/', info_page, {'page_slug': 'mission'}, name='mission'),
    path('quienes-somos/', info_page, {'page_slug': 'about'}, name='about'),
    path('academia-nisqa/', info_page, {'page_slug': 'academy'}, name='academy'),
    path('servicios/', info_page, {'page_slug': 'services'}, name='services'),
    path('tecnologia/', info_page, {'page_slug': 'technology'}, name='technology'),
    path('entradas/<slug:slug>/', post_detail, name='post_detail'),
]
