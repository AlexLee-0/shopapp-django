from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import Product


class LatestProductsFeed(Feed):
    title = "Магазин — последние продукты"
    link = "/shop/products/"
    description = "Свежие поступления"

    def items(self):
        return Product.objects.order_by("-created_at")[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse("shopapp:product_details", kwargs={"pk": item.pk})