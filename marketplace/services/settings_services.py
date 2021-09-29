# Модуль для работы с настройками проекта, такими как длительность кешей.
# Информация по актуальным настройкам хранится в JSON файле указанном в ACTUAL_SETTINGS_FILE
# Настройки по умолчанию храняться в JSON файле указанном в DEFAULT_SETTINGS_FILE
# При запуске проекта файл в актуальными настройками может не существовать, в таком случае при первом обращении к нему
# он будет создан с настройками по умолчанию по данным файла DEFAULT_SETTINGS_FILE
# Пример заполнения файла с настройками по умолчанию
# {
#     "categories_cache_timeout": 86400,
#     "banners_cache_timeout": 600,
#     "shops_cache_timeout": 86400,
#     "products_cache_timeout": 86400
# }
# Для добавления нового параметра к настройкам надо:
#  - добавить параметр в DEFAULT_SETTINGS_FILE
#  - удалить файл ACTUAL_SETTINGS_FILE
#  - добавить одноименный параметр в SettingModel
#  - реализоват функцию для получения этого параметра
#  - добавить в форму SettingForm(из setting.forms) новый параметр, по аналогии с существующими(указать нужные классы)
#  - если это параметр для длительности кеша, то реализовать метод для сброса этого кеша(всех кешей из этой группы);
# если этот кеш относится к модели, то сделать обработку сигнала post_save для сброса кеша этой модели; в
# модуле services.cache_services; задать в settings.py шаблон для ключа этого кеша. В форме из предыдущего пункта
# добавить поле для сброса группы этого кеша
#  - обновить функции set_actual_settings и delete_caches
# обновить инициализацию формы в методе SettingView.get_context_data в setting.views
import os

from django.utils.translation import gettext as _
from loguru import logger
from pydantic import BaseModel

from services.cache_services import delete_categories_cache, delete_banners_cache, delete_shops_cache, \
    delete_catalog_cache, delete_product_cache
from marketplace.settings import BASE_DIR
from setting.forms import SettingForm


DEFAULT_SETTINGS_FILE = os.path.join(BASE_DIR, 'marketplace', 'default_settings.json')
ACTUAL_SETTINGS_FILE = os.path.join(BASE_DIR, 'marketplace', 'settings.json')
ENCODING = 'UTF-8'

# TODO запись в лог файл


class SettingModel(BaseModel):
    """Класс модели настроек. Нужен для удобного парсинга JSON файла и преобразования в JSON"""

    categories_cache_timeout: int
    banners_cache_timeout: int
    shops_cache_timeout: int
    catalog_cache_timeout: int
    product_cache_timeout: int


def settings_file(func):
    """Декокатор для создания актуального файла настроек, если он не создан"""

    def wrapper():
        if not os.path.exists(ACTUAL_SETTINGS_FILE):
            logger.debug("json файла с настройками нет, создаём")
            create_actual_settings_json_file()
            logger.debug(f"Создан json файл с настройками по пути: {ACTUAL_SETTINGS_FILE}")
        return func()

    return wrapper


def create_actual_settings_json_file() -> None:
    """
    Метод для создания json файла с настройками.
    Создаётся файл по константе ACTUAL_SETTINGS_FILE, копируется информация из DEFAULT_SETTINGS_FILE
    """

    with open(DEFAULT_SETTINGS_FILE, mode='r', encoding=ENCODING) as default, \
            open(ACTUAL_SETTINGS_FILE, mode='w', encoding=ENCODING) as actual:
        default_settings = default.read()
        actual.write(default_settings)


def get_categories_cache_timeout() -> int:
    """Функция для получения timeout для кешей категорий"""

    return get_actual_settings().categories_cache_timeout


def get_banners_cache_timeout() -> int:
    """Функция для получения timeout для кешей баннеров"""

    return get_actual_settings().banners_cache_timeout


def get_shops_cache_timeout() -> int:
    """Функция для получения timeout для кешей продавцов"""

    return get_actual_settings().shops_cache_timeout


def get_catalog_cache_timeout() -> int:
    """Функция для получения timeout для кешей каталога"""

    return get_actual_settings().catalog_cache_timeout


def get_product_cache_timeout() -> int:
    """Функция для получения timeout для кешей товаров"""

    return get_actual_settings().product_cache_timeout


def get_cache_timeout(attr: str) -> int:
    """Функция для получения timeout кеша для переданного атрибута"""

    return getattr(get_actual_settings(), f'{attr}_cache_timeout')


@settings_file
def get_actual_settings() -> SettingModel:
    """Функция получения настроек из файла актуальных настроек"""

    settings_object = SettingModel.parse_file(ACTUAL_SETTINGS_FILE, encoding=ENCODING)
    return settings_object


def process_settings_page(setting_form: SettingForm) -> str:
    """Функция для обработки изменений на странице настроек"""
    message = ""
    message += set_actual_settings(setting_form)
    message += delete_caches(setting_form)
    return message


def set_actual_settings(setting_form: SettingForm) -> str:
    """Функция для установки актуальных настроек. Записывает данные в ACTUAL_SETTINGS_FILE.
    Возвращает сообщение для отображения"""

    actual_settings = SettingModel(
        categories_cache_timeout=setting_form.cleaned_data["categories_cache"],
        banners_cache_timeout=setting_form.cleaned_data["banners_cache"],
        shops_cache_timeout=setting_form.cleaned_data["shops_cache"],
        catalog_cache_timeout=setting_form.cleaned_data["catalog_cache"],
        product_cache_timeout=setting_form.cleaned_data["product_cache"],
    )
    with open(ACTUAL_SETTINGS_FILE, mode='w', encoding=ENCODING) as f:
        f.write(actual_settings.json(indent=4))

    logger.debug(f"categories_cache_timeout установлен в {actual_settings.categories_cache_timeout}")
    logger.debug(f"banners_cache_timeout установлен в {actual_settings.banners_cache_timeout}")
    logger.debug(f"shops_cache_timeout установлен в {actual_settings.shops_cache_timeout}")
    logger.debug(f"catalog_cache_timeout установлен в {actual_settings.catalog_cache_timeout}")
    logger.debug(f"product_cache_timeout установлен в {actual_settings.product_cache_timeout}")

    return _('Settings changed successfully')


def delete_caches(setting_form: SettingForm) -> str:
    """Функция для сброса указанных в форме кешей. Возвращает строку информацией по сброшенным кешам"""

    message = ''
    if setting_form.cleaned_data["delete_categories_cache"]:
        delete_categories_cache()
        logger.debug("Удалён кеш категорий")
        message += '<br>' + _('Deleted categories cache')

    if setting_form.cleaned_data["delete_banners_cache"]:
        delete_banners_cache()
        logger.debug("Удалён кеш баннеров")
        message += '<br>' + _('Deleted banners cache')

    if setting_form.cleaned_data["delete_shops_cache"]:
        delete_shops_cache()
        logger.debug("Удалён кеш продавцов")
        message += '<br>' + _('Deleted shops cache')

    if setting_form.cleaned_data["delete_catalog_cache"]:
        delete_catalog_cache()
        logger.debug("Удалён кеш продавцов")
        message += '<br>' + _('Deleted catalog cache')

    if setting_form.cleaned_data["delete_product_cache"]:
        delete_product_cache()
        logger.debug("Удалён кеш продавцов")
        message += '<br>' + _('Deleted product cache')

    return message
