import datetime
import os
import shutil
import sys

from django.core import serializers
from django.core.mail import send_mail
from loguru import logger
from main.models import ImportFiles
from marketplace.celery import app
from marketplace.settings import BASE_DIR

logger.add(sys.stderr, backtrace=True)
logger.add('imports/log_file.log', backtrace=True)

successful_imports = []
unsuccessful_imports = []


@app.task
def make_import(files, mail):
    for title, file in files.items():

        try:
            obj_generator = serializers.json.Deserializer(file)

            for obj in obj_generator:
                obj.save()

                log_import(obj.object, title)

            save_file(title, file, 'successful_imports')

        except Exception:

            save_file(title, file, 'unsuccessful_imports')

            log_import(file, title)

    global successful_imports, unsuccessful_imports
    successful_imports = ', '.join(successful_imports)
    unsuccessful_imports = ', '.join(unsuccessful_imports)
    send_mail(subject='imported_files',
              message=f'Hello. We want to tell you, that import of files was finished. Successful imports:\n{successful_imports}'
                      f'\nUnsuccessful imports:\n{unsuccessful_imports}',
              from_email='admin@myblog.com',
              recipient_list=[mail])


def log_import(object, title):
    if isinstance(object, str):
        logger.exception(f"In file {object} error occured {sys.exc_info()}", )

        global unsuccessful_imports
        unsuccessful_imports.append(title)

    else:
        logger.info(f'Was imported object of model {object.__class__.__name__}'
                    f' with id {object.id} at {datetime.datetime.now()} successfully')

        global successful_imports
        successful_imports.append(title)


def save_file(title, file, path):
    with open(f'imports/{path}/{title}', 'w', encoding='utf8') as saving_file:
        saving_file.write(file)
