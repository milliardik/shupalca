#!/usr/bin/env python3

from db_modules.db_models.base import *

class Asset(Model):
	host_name = CharField(max_length=100, unique=True, null=True)
	ip_address = CharField(max_length=45, unique=True, null=True)
	first_seen = DateTimeField()
	last_seen = DateTimeField(null=False, default=datetime.now())
	
	class Meta:
		database = db
		table_name = 'tbl_asset'