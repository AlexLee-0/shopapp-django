from string import ascii_letters
from random import choices
import json as json_lib

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Order, Product
from shopapp.utils import add_two_numbers


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="creator",
            password="testpass123",
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "123.45",
                "description": "product description",
                "discount": 10,
            },
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        # будет выполнено перед всеми тестами в классе
        cls.product = Product.objects.create(name="Best Product")

    @classmethod
    def tearDownClass(cls):
        # будет выполнено после всех тестов в классе
        cls.product.delete()

    # def setUp(self):
    #     # будет выполнено перед каждым тестом
    #     self.product = Product.objects.create(name="Best Product")
    #
    # def tearDown(self):
    #     # будет выполнено после каждого теста
    #     self.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse(
                'shopapp:product_details',
                kwargs={"pk": self.product.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_links(self):
        response = self.client.get(
            reverse(
                'shopapp:product_details',
                kwargs={"pk": self.product.pk},
            ),
        )
        self.assertContains(response, self.product.name)


class ProductsListTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
    ]

    def test_products(self):
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context['products']),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/products-list.html')


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse('shopapp:products-export'))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data,
        )


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test', password='test')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Заказы')
        self.assertTemplateUsed(response, "shopapp/order_list.html")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="order_viewer", password="test1234")
        view_order_perm = Permission.objects.get(
            codename="view_order", content_type__app_label="shopapp"
        )
        cls.user.user_permissions.add(view_order_perm)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address="г. Москва, ул. Ленина, д. 1",
            promocode="SALE10",
            user=self.user,
        )

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        url = reverse("shopapp:order_details", kwargs={"pk": self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context["object"].pk, self.order.pk)


class OrdersExportTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="staff_user",
            password="testpass123",
            is_staff=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)

        self.product1 = Product.objects.create(name="Товар 1", price=100)
        self.product2 = Product.objects.create(name="Товар 2", price=200)

        self.order1 = Order.objects.create(
            delivery_address="Адрес 1",
            promocode="PROMO1",
            user=self.user,
        )
        self.order1.products.add(self.product1)

        self.order2 = Order.objects.create(
            delivery_address="Адрес 2",
            promocode="PROMO2",
            user=self.user,
        )
        self.order2.products.add(self.product1, self.product2)

        self.order3 = Order.objects.create(
            delivery_address="Адрес 3",
            promocode="",
            user=self.user,
        )

    def tearDown(self):
        Order.objects.all().delete()
        Product.objects.all().delete()

    def test_orders_export(self):
        """Проверяем, что HTTP-ответ полностью совпадает с данными из БД."""
        url = reverse("shopapp:orders_export")
        response = self.client.get(url)

        # 1. Статус 200
        self.assertEqual(response.status_code, 200)

        # 2. Проверяем структуру и содержимое
        data = response.json()
        self.assertIn("orders", data)
        self.assertIsInstance(data["orders"], list)

        orders_db = Order.objects.order_by("pk")
        self.assertEqual(len(data["orders"]), orders_db.count())

        # 3. Сравниваем каждый заказ по полям
        for order_data, order_db in zip(data["orders"], orders_db):
            self.assertEqual(order_data["pk"], order_db.pk)
            self.assertEqual(order_data["delivery_address"], order_db.delivery_address)
            self.assertEqual(order_data["promocode"], order_db.promocode)
            self.assertEqual(order_data["user"], order_db.user_id)

            # products — сравнение с учётом порядка (сортируем)
            self.assertEqual(
                sorted(order_data["products"]),
                sorted(order_db.products.values_list("id", flat=True)),
            )
