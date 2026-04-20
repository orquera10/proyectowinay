from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.utils import timezone

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


def get_shared_context(current_page):
    ticker_items = list(
        Post.objects.filter(
            is_published=True,
            published_at__lte=timezone.now(),
        )[:6]
    )
    return {
        'nav_pages': NAV_PAGES,
        'current_page': current_page,
        'brand_banner_url': f"{settings.MEDIA_URL}winayBanner.png",
        'favicon_url': f"{settings.MEDIA_URL}winayLogo.png",
        'ticker_items': ticker_items or TICKER_FALLBACK,
    }


def home(request):
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
    posts_paginator = Paginator(posts, 6)
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
    context.update(get_shared_context('home'))
    return render(request, 'core/home.html', context)


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
