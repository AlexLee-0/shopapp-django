from django.test import TestCase
from django.urls import reverse


class RegisterViewTestCase(TestCase):
    def test_register_page(self):
        response = self.client.get(reverse("myauth:register"))
        self.assertEqual(response.status_code, 200)