# модуль методов скидок
from datetime import datetime

from django.db.models import QuerySet, Q

from main.models import Discount


def get_all_active_discounts() -> QuerySet[Discount]:
    """Функция для получения всех активных скидок"""

    active_discounts = Discount.objects.filter(
        Q(date_end__gt=datetime.now(), date_start__lt=datetime.now())
        | Q(date_end__gt=datetime.now(), date_start__isnull=True)).order_by("date_end")

    return active_discounts
