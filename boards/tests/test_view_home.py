from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from ..views import BoardListView
from ..models import Board




class HomeTests(TestCase):
    def setUp(self):  # created a Board instance to use in the tests & it will be deleter after test
        self.board = Board.objects.create(name='Django', description='Django Board')
        url = reverse('home') # setUp method is to store the things we use in other methods so we don't DRY
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEqual(self.response.status_code, 200) # test if this url response to get request withs status code of 200
    
    def test_home_url_resolves_home_view(self):
        view = resolve('/') # check if this url(the root url here) will fire/return the funtion(home) that he is suposed to run
        self.assertEqual(view.func.view_class, BoardListView) # since we used class based view
    
    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url)) # testing if the response has the text href="/boards/1/"
