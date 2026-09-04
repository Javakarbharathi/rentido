"""
Rentido config package.
Initializes PyMySQL as the MySQLdb driver for Django.
"""
import pymysql

pymysql.install_as_MySQLdb()

# This will ensure the app is always imported when Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)
