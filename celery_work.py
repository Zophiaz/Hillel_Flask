import os
import datetime
from celery import Celery
import alchemy_db
import models_db
from sqlalchemy.orm import Session
import requests_bank

rabbit_host = os.environ.get('RABBIT_HOST', 'localhost')
app = Celery('celery_work', broker=f'pyamqp://guest@{rabbit_host}//')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(86400.0, get_bank_data_task.s(), name='new currency data')


@app.task
def get_bank_data_task():
    requests_bank.get_privatbank_data()
    return True
