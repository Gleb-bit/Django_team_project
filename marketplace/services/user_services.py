# Модуль сервисов для работы с пользователями

from django.contrib.auth.models import User, AnonymousUser
from loguru import logger


ANONYMOUS_USERNAME = 'AnonymousUser'  # имя пользователя для работы с объектами анонимного пользователя
USER_PARAM_NAME = "user"


def _get_anonymous_user() -> User:
    """
    Функция для получения объекта User для работы с объектами анонимного пользователя.
    Если объекта ещё нет, то создаётся новый с username=ANONYMOUS_USERNAME
    Если
    """

    anonymous_user = User.objects.filter(username=ANONYMOUS_USERNAME).first()
    if not anonymous_user:
        anonymous_user = User.objects.create(username=ANONYMOUS_USERNAME)

    return anonymous_user


def handle_anonymous(function_to_decorate):
    """
    Декоратор для замены неавторизованного пользователя на объект модели User для работы с анонимом.
    Производит поиск и замену по аргументу user
    """
    def arguments_wrapper(*args, **kwargs):
        # print()
        # logger.debug("Вызов handle_anonymous")
        # logger.debug(f"function_to_decorate = {function_to_decorate.__name__}")
        # logger.debug(f"args={args}")
        # logger.debug(f"kwargs={kwargs}")
        # logger.debug(f"USER_PARAM_NAME in kwargs: {USER_PARAM_NAME in kwargs}")
        if USER_PARAM_NAME in kwargs and isinstance(kwargs[USER_PARAM_NAME], AnonymousUser):
            kwargs[USER_PARAM_NAME] = _get_anonymous_user()
            logger.debug(f"В функцию '{function_to_decorate.__name__}' в параметр '{USER_PARAM_NAME}' передан"
                         f" неавторизованный пользователь, заменён на объект User для работы с анонимами."
                         f" Параметры вызова функции:\nargs={args};\nkwargs={kwargs}\n")
        return function_to_decorate(*args, **kwargs)
    return arguments_wrapper


def get_user_by_username(username: str) -> User:
    """Функция для получения пользователя по имени пользователя"""

    return User.objects.get(username=username)
