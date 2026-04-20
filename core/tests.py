from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Post


class HomeViewTests(TestCase):
    def test_home_page_renders_successfully(self):
        response = self.client.get(reverse('core:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Winay')

    def test_home_page_uses_published_posts(self):
        post = Post.objects.create(
            title='Custodia VIP para eventos corporativos',
            excerpt='Entrada administrada desde Django admin.',
            body='Contenido extendido',
            is_featured=True,
            published_at=timezone.now(),
        )

        response = self.client.get(reverse('core:home'))

        self.assertContains(response, 'Custodia VIP para eventos corporativos')
        self.assertContains(response, 'Entrada administrada desde Django admin.')
        self.assertContains(response, post.get_absolute_url())

    def test_home_page_paginates_compact_posts_section(self):
        for index in range(7):
            Post.objects.create(
                title=f'Entrada {index}',
                excerpt=f'Resumen {index}',
                body='Contenido',
                published_at=timezone.now() - timezone.timedelta(minutes=index),
            )

        response = self.client.get(reverse('core:home'))
        second_page = self.client.get(reverse('core:home'), {'page': 2})

        self.assertContains(response, 'Entrada 0')
        self.assertContains(response, 'Entrada 5')
        self.assertNotContains(response, 'Entrada 6')
        self.assertContains(second_page, 'Entrada 6')

    def test_home_page_filters_posts_by_title(self):
        matching_post = Post.objects.create(
            title='Custodia avanzada',
            excerpt='Resumen 1',
            body='Contenido',
            published_at=timezone.now(),
        )
        non_matching_post = Post.objects.create(
            title='Monitoreo remoto',
            excerpt='Resumen 2',
            body='Contenido',
            published_at=timezone.now(),
        )

        response = self.client.get(reverse('core:home'), {'q': 'Custodia'})

        self.assertContains(response, 'Custodia avanzada')
        self.assertIn(matching_post, response.context['posts_page'].object_list)
        self.assertNotIn(non_matching_post, response.context['posts_page'].object_list)

    def test_post_detail_renders_published_post(self):
        post = Post.objects.create(
            title='Monitoreo estrategico',
            excerpt='Resumen del monitoreo.',
            body='Contenido de detalle del post.',
            published_at=timezone.now(),
        )

        response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contenido de detalle del post.')

    def test_post_detail_splits_body_into_paragraphs(self):
        post = Post.objects.create(
            title='Cobertura segmentada',
            excerpt='Resumen base.',
            body='Primer parrafo.\n\nSegundo parrafo.',
            published_at=timezone.now(),
        )

        response = self.client.get(post.get_absolute_url())

        self.assertContains(response, '<p>Primer parrafo.</p>', html=True)
        self.assertContains(response, '<p>Segundo parrafo.</p>', html=True)

    def test_post_detail_renders_hyphen_lines_as_bullets(self):
        post = Post.objects.create(
            title='Cobertura con items',
            excerpt='Resumen base.',
            body='Caracteristicas del servicio\n\n- Primer item\n- Segundo item',
            published_at=timezone.now(),
        )

        response = self.client.get(post.get_absolute_url())

        self.assertContains(response, '<h3>Caracteristicas del servicio</h3>', html=True)
        self.assertContains(response, '<li>Primer item</li>', html=True)
        self.assertContains(response, '<li>Segundo item</li>', html=True)

    def test_navbar_pages_render_successfully(self):
        pages = [
            ('core:mission', 'Mision y vision'),
            ('core:about', 'Quienes somos'),
            ('core:services', 'Servicios'),
            ('core:technology', 'Tecnologia'),
        ]

        for url_name, label in pages:
            with self.subTest(page=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, label)

    def test_ticker_renders_on_internal_pages(self):
        post = Post.objects.create(
            title='Novedad institucional',
            excerpt='Seguimiento operativo permanente.',
            body='Contenido',
            published_at=timezone.now(),
        )

        mission_response = self.client.get(reverse('core:mission'))
        detail_response = self.client.get(post.get_absolute_url())

        self.assertContains(mission_response, 'Novedad institucional')
        self.assertContains(detail_response, 'Novedad institucional')
