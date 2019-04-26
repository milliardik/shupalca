#!/usr/bin/env python3

from datetime import date, datetime
from peewee import MySQLDatabase, Model
from peewee import CharField, IntegerField, BooleanField, ForeignKeyField, DateTimeField, DateField

db = MySQLDatabase('shupalca', user='shup_adm', password='shupadmin_1')#, host='localhost', port=3316)