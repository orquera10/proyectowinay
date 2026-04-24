import os
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils import timezone

from .forms import ContactForm
from .models import Post


NAV_PAGES = [
    {'slug': 'home', 'title': 'Inicio', 'url_name': 'core:home'},
    {'slug': 'mission', 'title': 'Mision', 'url_name': 'core:mission'},
    {'slug': 'academy', 'title': 'Academia Nisqa', 'external_url': 'https://institutonisqa.com/'},
    {'slug': 'news', 'title': 'Novedades', 'url_name': 'core:home', 'fragment': 'novedades'},
]


TICKER_FALLBACK = [
    {
        'title': 'Educacion, cultura y acompanamiento comunitario.',
        'excerpt': 'Impulsamos oportunidades para el desarrollo humano integral.',
    },
    {
        'title': 'Trabajo en red con instituciones y familias.',
        'excerpt': 'Fortalecemos procesos colectivos desde la cercania y la escucha.',
    },
    {
        'title': 'Compromiso con un futuro justo y sostenible.',
        'excerpt': 'Cada accion busca dejar capacidades instaladas en la comunidad.',
    },
]


INFO_PAGES = {
    'mission': {
        'title': 'Mision y vision',
        'eyebrow': 'Direccion institucional',
        'intro': 'Crecimiento eterno con impacto humano.',
        'lead': 'La Fundacion Winay - Crecimiento Eterno es una institucion sin fines de lucro comprometida con el bienestar de comunidades vulnerables en la provincia de Jujuy. Nuestra mision es contribuir a la mejora de la calidad de vida mediante una labor educativa, social, cultural y recreativa que promueva un desarrollo humano integral y sostenible.',
        'sections': [
            {
                'title': 'Mision',
                'body': 'Mediante una gestion responsable de nuestros recursos, fortalecemos las potencialidades, habilidades y destrezas de ninos, ninas, adolescentes y personas adultas, con el objetivo de generar oportunidades que impulsen su crecimiento personal y colectivo.',
            },
            {
                'title': 'Vision',
                'body': 'Aspiramos a consolidar una comunidad mas justa y equitativa, donde la educacion, la solidaridad y el trabajo conjunto actuen como motores de transformacion sostenida en cada territorio que acompanamos.',
            },
        ],
    },
    'about': {
        'title': 'Quienes somos',
        'eyebrow': 'Identidad Winay',
        'intro': 'Una fundacion nacida para acompanar y potenciar.',
        'lead': 'En Fundacion Winay trabajamos desde una mirada cercana, respetuosa y profundamente humana. Nos guia la conviccion de que cada persona y cada comunidad poseen capacidades valiosas que pueden fortalecerse cuando existen oportunidades, acompanamiento y redes de apoyo.',
        'sections': [
            {
                'title': 'Valores que nos orientan',
                'body': 'Nos regimos por el respeto a la dignidad humana, la excelencia en nuestras acciones y el compromiso de brindar respuestas concretas a los desafios que atraviesan las comunidades con las que trabajamos.',
            },
            {
                'title': 'Trabajo con la comunidad',
                'body': 'Construimos procesos junto a familias, referentes territoriales, instituciones y voluntariado, entendiendo que los cambios duraderos nacen de la escucha, la participacion y la corresponsabilidad.',
            },
        ],
    },
    'academy': {
        'title': 'Academia Nisqa',
        'eyebrow': 'Formacion y futuro',
        'intro': 'Aprender tambien es transformar.',
        'lead': 'Academia Nisqa es un espacio de formacion y acompanamiento que nace para fortalecer habilidades, despertar vocaciones y ampliar oportunidades por medio de propuestas educativas y comunitarias con identidad territorial.',
        'sections': [
            {
                'title': 'Trayectorias de aprendizaje',
                'body': 'Promovemos espacios de apoyo, refuerzo y orientacion para que cada participante pueda sostener su proceso educativo con mayor confianza y herramientas concretas.',
            },
            {
                'title': 'Habilidades para la vida',
                'body': 'Trabajamos habilidades personales, sociales y comunitarias que fortalecen la autonomia, la participacion y la construccion de proyectos con sentido.',
            },
            {
                'title': 'Puentes con la comunidad',
                'body': 'La academia se articula con familias, instituciones y referentes para que la formacion no quede aislada, sino conectada con oportunidades reales de desarrollo.',
            },
        ],
    },
    'technology': {
        'title': 'Articulacion',
        'eyebrow': 'Redes y sostenibilidad',
        'intro': 'Nadie transforma en soledad.',
        'lead': 'Sostenemos nuestro trabajo a partir de la articulacion con actores publicos, privados y comunitarios que comparten la busqueda de una sociedad mas inclusiva, solidaria y con mejores oportunidades.',
        'sections': [
            {
                'title': 'Alianzas institucionales',
                'body': 'Promovemos convenios y acciones compartidas con escuelas, organizaciones sociales, equipos tecnicos y referentes locales para ampliar el alcance de nuestras intervenciones.',
            },
            {
                'title': 'Participacion comunitaria',
                'body': 'Favorecemos la construccion de espacios de encuentro donde la comunidad pueda proponer, involucrarse y ser protagonista de las soluciones.',
            },
            {
                'title': 'Sostenibilidad de los procesos',
                'body': 'Cuidamos los recursos y planificamos cada accion con responsabilidad, buscando que el impacto sea duradero y deje capacidades instaladas en el territorio.',
            },
        ],
    },
}


def get_shared_context(current_page, contact_form=None):
    ticker_items = list(
        Post.objects.filter(
            is_published=True,
            published_at__lte=timezone.now(),
        )[:6]
    )
    return {
        'nav_pages': NAV_PAGES,
        'current_page': current_page,
        'brand_banner_url': f"{settings.STATIC_URL}winayBanner.png",
        'brand_banner_mobile_url': f"{settings.STATIC_URL}logoCel.png",
        'favicon_url': f"{settings.STATIC_URL}winayLogo.png",
        'ticker_items': ticker_items or TICKER_FALLBACK,
        'social_links': [
            {
                'name': 'Instagram',
                'url': os.getenv('INSTAGRAM_URL', 'https://www.instagram.com/fundacionwinay'),
                'handle': os.getenv('INSTAGRAM_HANDLE', '@fundacionwinay'),
                'cta': 'Seguinos en Instagram',
            },
            {
                'name': 'Facebook',
                'url': os.getenv('FACEBOOK_URL', 'https://www.facebook.com/tupagina'),
                'handle': os.getenv('FACEBOOK_HANDLE', 'Fundacion Winay'),
                'cta': 'Seguinos en Facebook',
            },
        ],
        'contact_email': os.getenv('CONTACT_EMAIL', 'contacto@winay.local'),
        'contact_phone': os.getenv('CONTACT_PHONE', '+54 000 000 0000'),
        'contact_form': contact_form or ContactForm(),
    }


def build_home_context(request, contact_form=None):
    posts = Post.objects.filter(
        is_published=True,
        published_at__lte=timezone.now(),
    )
    search_query = request.GET.get('q', '').strip()
    if search_query:
        posts = posts.filter(title__icontains=search_query)
    featured_posts = list(posts.filter(is_featured=True)[:6])
    if len(featured_posts) < 6:
        featured_ids = {post.pk for post in featured_posts}
        supplemental_posts = posts.exclude(pk__in=featured_ids)[: 6 - len(featured_posts)]
        featured_posts.extend(supplemental_posts)
    recent_posts = list(posts[:6])
    posts_paginator = Paginator(posts, 8)
    posts_page = posts_paginator.get_page(request.GET.get('page'))

    fallback_services = [
        {
            'eyebrow': 'Educacion',
            'title': 'Espacios que fortalecen aprendizajes y trayectorias',
            'description': 'Acompanamos a ninas, ninos y adolescentes con propuestas que cuidan, orientan y abren oportunidades.',
            'tone': 'primary',
            'banner_image_url': '',
            'published_at': None,
        },
        {
            'eyebrow': 'Comunidad',
            'title': 'Redes de apoyo para crecer con dignidad y autonomia',
            'description': 'Impulsamos encuentros, acompanamiento social y articulacion con familias e instituciones.',
            'tone': 'secondary',
            'banner_image_url': '',
            'published_at': None,
        },
        {
            'eyebrow': 'Cultura',
            'title': 'Actividades recreativas y culturales con sentido comunitario',
            'description': 'Creamos espacios participativos que fortalecen el vinculo social y la expresion colectiva.',
            'tone': 'accent',
            'banner_image_url': '',
            'published_at': None,
        },
    ]

    capabilities = [
        'Acompanamiento educativo y comunitario',
        'Acciones sociales, culturales y recreativas',
        'Trabajo articulado con familias e instituciones',
        'Gestion responsable orientada a impacto sostenible',
    ]

    metrics = [
        {'value': 'Jujuy', 'label': 'Compromiso territorial con las comunidades de la provincia'},
        {'value': 'Integral', 'label': 'Mirada educativa, social, cultural y recreativa'},
        {'value': 'Humano', 'label': 'Trabajo basado en dignidad, escucha y corresponsabilidad'},
    ]

    fallback_recent = [
        {
            'title': 'Proyectos que fortalecen el crecimiento personal y colectivo',
            'excerpt': 'Cada iniciativa se piensa para abrir oportunidades y sostener procesos con impacto real.',
            'published_at': None,
        },
        {
            'title': 'Trabajo junto a familias, instituciones y referentes territoriales',
            'excerpt': 'La red comunitaria es parte esencial de cada propuesta que impulsamos.',
            'published_at': None,
        },
        {
            'title': 'Educacion y solidaridad como motores de transformacion',
            'excerpt': 'Sostenemos acciones concretas con una mirada justa, participativa y sostenible.',
            'published_at': None,
        },
    ]

    context = {
        'featured_services': featured_posts or fallback_services,
        'capabilities': capabilities,
        'metrics': metrics,
        'recent_highlights': recent_posts or fallback_recent,
        'posts_page': posts_page,
        'search_query': search_query,
    }
    context.update(get_shared_context('home', contact_form=contact_form))
    return context


def home(request):
    return render(request, 'core/home.html', build_home_context(request))


def contact_submit(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    form = ContactForm(request.POST)
    redirect_to = request.POST.get('next') or reverse('core:home')

    if not form.is_valid():
        messages.error(request, 'Revisa el formulario de contacto y completa los campos requeridos.')
        if redirect_to == reverse('core:home'):
            return render(request, 'core/home.html', build_home_context(request, contact_form=form))
        return redirect(redirect_to)

    contact_email = os.getenv('CONTACT_EMAIL', 'contacto@winay.local')
    name = form.cleaned_data['name']
    sender_email = form.cleaned_data['email']
    phone = form.cleaned_data['phone'].strip()
    phone_display = phone or 'No indicado'
    subject = form.cleaned_data['subject']
    message = form.cleaned_data['message']
    plain_message = '\n'.join(
        [
            'Nuevo mensaje recibido desde la web de Fundacion Winay',
            '',
            f'Nombre: {name}',
            f'Email: {sender_email}',
            f'Telefono: {phone_display}',
            f'Asunto: {subject}',
            '',
            'Mensaje:',
            message,
        ]
    )
    html_message = f"""
    <div style="font-family:Arial,sans-serif;color:#163247;line-height:1.6">
        <div style="max-width:620px;border:1px solid #dceef8;border-radius:18px;overflow:hidden">
            <div style="background:#2c7fb8;color:#ffffff;padding:18px 22px">
                <h2 style="margin:0;font-size:20px">Nuevo mensaje desde la web</h2>
                <p style="margin:6px 0 0;color:#e8f6ff">Fundacion Winay</p>
            </div>
            <div style="padding:22px;background:#f8fcff">
                <p style="margin:0 0 16px">Una persona completo el formulario de contacto.</p>
                <table style="width:100%;border-collapse:collapse;margin-bottom:20px">
                    <tr>
                        <td style="padding:8px 0;color:#587186;width:110px">Nombre</td>
                        <td style="padding:8px 0;font-weight:bold">{escape(name)}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px 0;color:#587186">Email</td>
                        <td style="padding:8px 0"><a href="mailto:{escape(sender_email)}">{escape(sender_email)}</a></td>
                    </tr>
                    <tr>
                        <td style="padding:8px 0;color:#587186">Telefono</td>
                        <td style="padding:8px 0">{escape(phone_display)}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px 0;color:#587186">Asunto</td>
                        <td style="padding:8px 0">{escape(subject)}</td>
                    </tr>
                </table>
                <div style="border-top:1px solid #dceef8;padding-top:16px">
                    <strong style="display:block;margin-bottom:8px">Mensaje</strong>
                    <div style="white-space:pre-wrap;background:#ffffff;border:1px solid #dceef8;border-radius:14px;padding:14px">{escape(message)}</div>
                </div>
            </div>
        </div>
    </div>
    """

    try:
        email = EmailMultiAlternatives(
            subject=f'[Web Winay] {subject}',
            body=plain_message,
            from_email=os.getenv('DEFAULT_FROM_EMAIL', contact_email),
            to=[contact_email],
            reply_to=[sender_email],
        )
        email.attach_alternative(html_message, 'text/html')
        email.send(fail_silently=False)
    except Exception:
        messages.warning(
            request,
            'Recibimos tu mensaje, pero el envio automatico no esta configurado todavia. Usa el email de contacto mientras terminamos esa integracion.',
        )
    else:
        messages.success(request, 'Tu mensaje fue enviado correctamente. Gracias por escribirnos.')

    return redirect(redirect_to)


def post_detail(request, slug):
    post = get_object_or_404(
        Post,
        slug=slug,
        is_published=True,
        published_at__lte=timezone.now(),
    )
    recent_posts = Post.objects.filter(
        is_published=True,
        published_at__lte=timezone.now(),
    ).exclude(pk=post.pk)[:3]
    context = {
        'post': post,
        'recent_posts': recent_posts,
    }
    context.update(get_shared_context(''))
    return render(request, 'core/post_detail.html', context)


def info_page(request, page_slug):
    page = INFO_PAGES[page_slug].copy()
    context = {'page': page}
    context.update(get_shared_context(page_slug))
    return render(request, 'core/info_page.html', context)
