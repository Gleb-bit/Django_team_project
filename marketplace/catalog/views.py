import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import QuerySet, Count, Min, Max
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, FormView, CreateView
from loguru import logger

from catalog.forms import ReviewCreateForm
from marketplace.settings import CATALOG_CACHE_KEY_TEMPLATE, PRODUCT_CACHE_KEY_TEMPLATE
from marketplace.views import BaseMixin
from main.models import Product, Warehouse, Shop, Category
from services.settings_services import get_cache_timeout
from services.utils import RecentProductsEngine


class CatalogListView(BaseMixin, ListView):
    """ Представление каталога товаров """
    template_name = 'catalog/catalog_list.html'
    queryset = Product.objects.filter(is_active=True)
    paginate_by = 6

    sells_sort_dec = True
    price_sort_dec = True
    reviews_sort_dec = True
    released_sort_dec = True

    def dispatch(self, request, *args, **kwargs):
        current_sorting = self.request.GET.get('sort')
        if current_sorting:
            logger.debug(f'Переопределение направления сортировки. Текущее значение: {current_sorting}')
            key = current_sorting[:-3]
            direction = True if current_sorting[-3:] == 'dec' else False
            setattr(self, f'{key}_sort_dec', not direction)
        return super(CatalogListView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def process_filter(queryset: QuerySet[Product], key: str, value: str) -> QuerySet[Product]:
        """
        Обработка фильтров запроса
        :param queryset: изначальный результат запроса
        :param key: поле для фильтрации
        :param value: значение фильтрации
        :return: отфильтрованный результат запроса
        """
        if key == 'price':
            logger.debug(f'Фильтрация по цене. Значение: {value}')
            values = tuple(value.split(';'))
            return queryset.filter(warehouse__price__range=values)
        elif key == 'shop':
            if value == 'none':
                return queryset
            else:
                logger.debug(f'Фильтрация по магазину. Значение: {value}')
                return queryset.filter(warehouse__shop__name=value)
        elif key == 'available':
            logger.debug(f'Фильтрация по наличию на складах.')
            return queryset.filter(warehouse__amount__gt=0)
        elif key == 'free_shipping':
            logger.debug(f'Фильтрация по возможности бесплатной доставки')
            return queryset.filter(warehouse__free_shipping=True)
        elif key == 'category':
            logger.debug(f'Фильтрация по категории. Значение: {value}')
            category = Category.objects.get(name=value)
            categories = [category]
            for subcategory in category.children_categories.all():
                categories.append(subcategory)
            return queryset.filter(category__in=categories)
        elif key == 'name' and value == '':
            return queryset
        elif key == 'name':
            logger.debug(f'Фильтрация по названию. Значение: {value}')
            return queryset.filter(name=value)
        else:
            return queryset

    @staticmethod
    def process_sort(queryset: QuerySet[Product], key: str) -> QuerySet[Product]:
        """
        Обработка сортировки запроса
        :param queryset: изначальный результат запроса
        :param key: поле для сортировки
        :return: отфильтрованный результат запроса
        """
        if key.startswith('price'):
            logger.debug(f'Сортировка по цене. Направление: {key[-3:]}')
            queryset = queryset.annotate(discounted_price=Min('warehouse__discounted_price'))
            if key.endswith('dec'):
                queryset = queryset.order_by('-discounted_price')
            elif key.endswith('inc'):
                queryset = queryset.order_by('discounted_price')
        elif key.startswith('reviews'):
            logger.debug(f'Сортировка по количеству отзывов. Направление: {key[-3:]}')
            if key.endswith('dec'):
                queryset = queryset.annotate(num_reviews=Count('reviews')).order_by('-num_reviews')
            elif key.endswith('inc'):
                queryset = queryset.annotate(num_reviews=Count('reviews')).order_by('num_reviews')
        else:
            logger.debug(f'Сортировка. Значение: {key}')
            if key.endswith('dec'):
                queryset = queryset.order_by('-' + key[:-3])
            elif key.endswith('inc'):
                queryset = queryset.order_by(key[:-3])
        return queryset

    @staticmethod
    def trim_sort_path(path: str) -> str:
        """
        Подготовка ссылки для сортировки
        :param path: изначальная ссылка
        :return: отредактированная ссылка
        """
        logger.debug(f'Подготовка ссылки для сортировки. path: {path}')
        result = re.sub(r'[?&]page=\w+', '', path)
        result = re.sub(r'[?&]sort=\w+', '', result)
        if result.endswith('/'):
            result += '?'
        else:
            result += '&'
        return result

    @staticmethod
    def trim_page_path(path: str) -> str:
        """
        Подготовка ссылки для пагинации
        :param path: изначальная ссылка
        :return: отредактированная ссылка
        """
        logger.debug(f'Подготовка ссылки для пагинации. path: {path}')
        result = re.sub(r'[?&]page=\w+', '', path)
        if result.endswith('/'):
            result += '?'
        else:
            result += '&'
        return result

    def get_queryset(self):
        logger.debug(f'Получение результата запроса товаров каталога')
        queryset = super(CatalogListView, self).get_queryset().order_by('-sort_index')
        catalog_key = CATALOG_CACHE_KEY_TEMPLATE.format(self.request.user.username)
        for key, value in self.request.GET.items():
            if key == 'sort' or key == 'page':
                continue
            else:
                queryset = self.process_filter(queryset, key, value)
                logger.debug(f"queryset '{queryset}' после фильтра {key} {value}")
                catalog_key += f':{key}-{value}'

        sort_by = self.request.GET.get('sort')
        if sort_by:
            queryset = self.process_sort(queryset, sort_by)
            catalog_key += f':{sort_by}'

        queryset = cache.get_or_set(catalog_key, queryset, get_cache_timeout('catalog'))
        return queryset.distinct()

    def get_initials_for_form(self, context: dict) -> dict:
        """
        Инициализация полей формы фильтрации
        :param context: изначальный объект контекста
        :return: отредактированный объект контекста
        """
        logger.debug(f'Инициализация полей формы фильтрации')
        price = self.request.GET.get('price')
        if price:
            prices = price.split(';')
            context['initial_min_price'] = prices[0]
            context['initial_max_price'] = prices[1]
        else:
            context['initial_min_price'] = context['min_price']
            context['initial_max_price'] = context['max_price']
        context['initial_name'] = self.request.GET.get('name') or ''
        context['selected_shop'] = self.request.GET.get('shop') or None
        context['initial_available'] = self.request.GET.get('available') or None
        context['initial_free_shipping'] = self.request.GET.get('free_shipping') or None
        return context

    def get_sort_direction(self, context: dict) -> dict:
        """
        Получение контекста о направлении сортировки для ссылок сортировки
        :param context: изначальный объект контекста
        :return: отредактированный объект контекста
        """
        logger.debug(f'Получение контекста о направлении сортировки для ссылок сортировки')
        context['sells_direction'] = 'dec' if self.sells_sort_dec else 'inc'
        context['price_direction'] = 'dec' if self.price_sort_dec else 'inc'
        context['reviews_direction'] = 'dec' if self.reviews_sort_dec else 'inc'
        context['released_direction'] = 'dec' if self.released_sort_dec else 'inc'
        return context

    def get_context_data(self, **kwargs):
        logger.debug(f'Получение контекста страницы каталога')
        context = super(CatalogListView, self).get_context_data(**kwargs)
        context['min_price'] = int(self.queryset.aggregate(Min('warehouse__price'))['warehouse__price__min'])
        context['max_price'] = int(self.queryset.aggregate(Max('warehouse__price'))['warehouse__price__max'])
        context['shops'] = Shop.objects.all()
        context['sort_path'] = self.trim_sort_path(self.request.get_full_path())
        context['page_path'] = self.trim_page_path(self.request.get_full_path())
        context = self.get_initials_for_form(context)
        context = self.get_sort_direction(context)

        return context


class FilterFormView(FormView):
    """ Представление формы фильтрации """
    def post(self, request, *args, **kwargs):
        logger.debug(f'Отправка запроса фильтрации')
        args = []
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                args.append(f'{key}={value}')
        return redirect(f'{reverse("catalog")}?{"&".join(args)}')


class ReviewCreateView(BaseMixin, CreateView):
    """ Представление формы создания отзывов """
    form_class = ReviewCreateForm
    template_name = 'catalog/product.html'

    def form_valid(self, form):
        logger.debug(f'Форма создания отзыва валидна')
        self.object = form.save(commit=False)
        self.object.product = Product.objects.get(slug=self.kwargs['slug'])
        self.object.save()
        logger.info(f'Отзыв на товар "{self.object.product}" создан. email: {self.object.email}')
        return redirect(self.get_success_url())

    def render_to_response(self, context, **response_kwargs):
        context['object'] = Product.objects.get(slug=self.kwargs['slug'])
        return super(ReviewCreateView, self).render_to_response(context, **response_kwargs)


class ProductDetailView(BaseMixin, DetailView):
    """ Представление детальной страницы товара """
    template_name = 'catalog/product.html'
    model = Product

    def get(self, request, *args, **kwargs):
        product = Product.objects.get(slug=self.kwargs['slug'])
        logger.debug(f'Получение представления детальной страницы товара "{product}"')
        product_key = PRODUCT_CACHE_KEY_TEMPLATE.format(product.slug)
        product = cache.get_or_set(product_key, product, get_cache_timeout('product'))
        logger.debug(f'Добавление товара "{product}" в недавно просмотренные')
        RecentProductsEngine.add_recent_product(self.request.user, product)
        return super(ProductDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        logger.debug(f'Получение контекста детальной страницы товара "{self.object}"')
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['warehouses'] = Warehouse.objects.filter(product=self.object).filter(amount__gt=0)
        num_reviews = self.request.GET.get('more_reviews')
        if num_reviews:
            num_reviews = int(num_reviews)
            context['more_reviews'] = num_reviews + 5
        else:
            num_reviews = 5
            context['more_reviews'] = 10
        context['reviews'] = self.object.reviews.all()[:num_reviews]
        context['form'] = ReviewCreateForm
        return context


class AddRecentProductView(LoginRequiredMixin, View):
    """ Представление добавления товара в недавно просмотренные """
    login_url = '/login'

    def get(self, request, *args, **kwargs):
        product = Product.objects.get(slug=kwargs['slug'])
        logger.debug(f'Добавление товара "{product}" в недавно просмотренные')
        RecentProductsEngine.add_recent_product(request.user, product)
        return redirect(request.META.get('HTTP_REFERER') or reverse('catalog'))


def calculate_all_discounted_prices(request):
    """
    Обновление всех скидок для всех товаров
    :param request: объект запроса
    :return: перенаправление на домашнюю страницу
    """
    logger.debug(f'Обновление всех скидок для всех товаров')
    warehouses = Warehouse.objects.all()
    for warehouse in warehouses:
        if warehouse.product.is_discounted():
            discount = warehouse.product.get_best_discount()
            if discount.shop == warehouse.shop or discount.shop is None:
                warehouse.discounted_price = round(warehouse.price * (100 - discount.percent) / 100, 2)
            else:
                warehouse.discounted_price = warehouse.price
        else:
            warehouse.discounted_price = warehouse.price
        warehouse.save()
    return redirect('/')
