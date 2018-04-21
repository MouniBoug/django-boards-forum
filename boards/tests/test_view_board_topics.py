from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from ..views import TopicListView, new_topic
from ..models import Board


class BoardTopicsTest(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django Board')

    def test_board_topics_view_success_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 65})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve('/boards/1/')
        self.assertEqual(view.func.view_class, TopicListView)

    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        homepage_url = reverse('home')

        response = self.client.get(board_topics_url)

        self.assertContains(response, 'href="{0}"'.format(new_topic_url))
        self.assertContains(response, 'href="{0}"'.format(homepage_url))
