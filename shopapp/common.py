from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(file, encoding=encoding)
    reader = DictReader(csv_file)

    # Ожидаемые поля
    expected_fields = {"name", "description", "price", "discount"}

    # Проверяем, что первая строка — заголовки
    if reader.fieldnames is None:
        raise ValueError("CSV-файл пустой или не содержит заголовков.")

    # Убираем BOM, если есть
    reader.fieldnames = [name.strip().lstrip("\ufeff") for name in reader.fieldnames]

    if not expected_fields.issubset(set(reader.fieldnames)):
        raise ValueError(
            f"CSV должен содержать поля: {expected_fields}. "
            f"Найдены: {reader.fieldnames}. "
            f"Проверьте, что разделитель — запятая, а кодировка — UTF-8."
        )

    products = []
    for row in reader:
        # Пропускаем пустые строки
        if not any(v.strip() for v in row.values() if v):
            continue

        # Приводим значения к нужным типам
        products.append(
            Product(
                name=row["name"].strip(),
                description=row.get("description", "").strip(),
                price=row.get("price", "0").strip() or "0",
                discount=row.get("discount", "0").strip() or "0",
            )
        )

    Product.objects.bulk_create(products)
    return products
