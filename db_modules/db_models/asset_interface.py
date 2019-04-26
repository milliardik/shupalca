#!/usr/bin/env python3
from db_modules.db_models.base import *
from db_modules.db_models.asset_inventory_models import AssetInventory

		
class IfMode(Model):
	mode_name = CharField(max_length=45, unique=True, null=False)
	
	class Meta:
		database = db
		table_name = 'tbl_interface_mode'
	
class IfVlan(Model):
	vlan_num = IntegerField(unique=True, null=False)
	description = CharField(max_length=100, null=True, default=None)
	
	class Meta:
		database = db
		table_name = 'tbl_vlan'

class AssetInterface(Model):
	if_index = CharField(max_length=6, null=False)#IntegerField(unique=True, null=False)
	if_name = CharField(max_length=60, null=False)
	description = CharField(max_length=150, null=True)
	oper_status = BooleanField(null=False, default=0)
	admin_status = BooleanField(null=False, default=1)
	mode_id = ForeignKeyField(IfMode, backref='mode', null=True)
	asset_id = ForeignKeyField(AssetInventory, backref='asset', null=False)
	vlan_id = ForeignKeyField(IfVlan, backref='vlan', null=False)
	is_physical = BooleanField(null=False, default=1)
	
	class Meta:
		database = db
		table_name = 'tbl_asset_interface'

	