import datetime
from peewee import DoesNotExist
from db_modules.db_models.base import db
from db_modules.db_models.asset_inventory_models import AssetModel, AssetFirmware, AssetManufacturer, AssetType, AssetInventory
from db_modules.db_models.asset_models import Asset
from db_modules.db_models.asset_interface import AssetInterface, IfMode, IfVlan


class DbAssetObj():
	
	def __init__(self, host_name, ip_address):
		try:
			self.asset = Asset.get(Asset.host_name == host_name)
			asset_inventory_query = AssetInventory.select().where(AssetInventory.asset_id == self.asset)
			asset_ports_query = AssetInterface.select(AssetInterface.if_index).where(AssetInterface.asset_id == self.asset)
			self.inventory_list = [asset_inventory for asset_inventory in asset_inventory_query]
			self.ports = {port.if_index:DbAssetInterface(self.asset.id, port.if_index) for port in asset_ports_query}
			self.in_db = True
		except DoesNotExist:
			self.asset = Asset(host_name = host_name,
							   ip_address = ip_address)
			self.inventory_list = []
			self.ports = {}
			self.in_db = False
		
	
	def get_id(self):
		return self.asset.id
	
	def create(self, asset_data):#inventory_datas):
		self.asset.first_seen = datetime.datetime.now()
		self.asset.save()
		
		asset_inventory_data = asset_data.get('inventory_data')
		asset_ports_data = asset_data.get('ports')
		
		
		for inventory_data in asset_inventory_data:
			asset_inventory_obj = DbAssetInventory(inventory_data.get('serial_num'))
			if not asset_inventory_obj.in_db:
				inventory_data['asset_id'] = self.asset
				asset_inventory_obj.create(inventory_data)
			else:
				asset_inventory_obj.update(asset_id = self.asset)
			
			self.inventory_list.append(asset_inventory_obj)

		for port in asset_ports_data.values():
			port.update({'asset_id':self.asset})
			port_db_obj = DbAssetInterface(self.asset, port['if_index'])
			port_db_obj.create(port)
			self.ports[port_db_obj.if_index] = port_db_obj
			
		return True
		
	
	def update(self, asset_data):
		query = Asset.update(last_seen = datetime.datetime.now()).where(Asset.id == self.asset)
		query.execute()
		
		ports_data = asset_data['ports'] 
		for port_data in ports_data.values():
			if_index = port_data.pop('if_index')
			self.ports[if_index].update(port_data) 
		
		return True
		
	def delete(self):
		self.asset.delete_instance()
		self.asset = None
		self.in_db = False

	def get_asset_serial_nums(self):
		serial_nums = []
		for asset_inventory in self.inventory_list:
			serial_nums.append(asset_inventory.serial_num)
		return serial_nums
		
	def __eq__(self, other):
		serial_nums_set_1 = self.get_asset_serial_nums()
		serial_nums_set_2 = other.get_asset_serial_nums()
		bool_list = list(map(lambda x,y : x==y, serial_nums_set_1, serial_nums_set_2))
		
		if len(serial_nums_set_1) == len(serial_nums_set_2) and all(bool_list):
			return True
		
		return False

class DbAssetInventory():

	def __init__(self, serial_num):
		self.serial_num = serial_num
		try:
			self.asset_inventory = AssetInventory.get(AssetInventory.serial_num == serial_num)
			self.in_db = True
		except DoesNotExist:
			self.in_db = False
			
			
	def create(self, inventory_data):		
		inventory_data['manufacturer_id'], _ = AssetManufacturer.get_or_create(manufacturer_name=inventory_data.pop('manufacturer'))
		inventory_data['model_id'], _ = AssetModel.get_or_create(model_name=inventory_data.pop('model'))
		inventory_data['firmware_id'], _ = AssetFirmware.get_or_create(firmware_name=inventory_data.pop('firmware'))
		inventory_data['type_id'], _ = AssetType.get_or_create(type_name=inventory_data.pop('type'))

		self.asset_inventory = AssetInventory.create(**inventory_data)
		
	def get_id(self):
		return self.asset_inventory.id
		
	def delete(self):
		pass
		
	def update(self, **kwargs):
		query = AssetInventory.update(**kwargs).where(AssetInventory.serial_num == self.serial_num)
		query.execute()

class DbAssetInterface():
	def __init__(self, asset_id, if_index):
		self.asset_id = asset_id
		self.if_index = if_index
		try:
			self.port = AssetInterface.get(AssetInterface.asset_id == asset_id, AssetInterface.if_index == if_index)
			self.in_db = True
		except DoesNotExist:
			self.in_db = False
			
			
	def create(self, if_data):
		if_data['vlan_id'], _ = IfVlan.get_or_create(vlan_num = if_data.pop('vlan'))
		if_data['mode_id'], _ = IfMode.get_or_create(mode_name = if_data.pop('mode'))
		if_data.update({'asset_id':self.asset_id})
		self.port = AssetInterface(**if_data)
		return self.port.save()
	
	def update(self, if_data):
		if_data['vlan_id'], _ = IfVlan.get_or_create(vlan_num = if_data.pop('vlan'))
		if_data['mode_id'], _ = IfMode.get_or_create(mode_name = if_data.pop('mode'))
		query = AssetInterface.update(**if_data).where(AssetInterface.asset_id == self.asset_id, AssetInterface.if_index == self.if_index)
		query.execute()
		self.port = AssetInterface.get(AssetInterface.asset_id == self.asset_id, AssetInterface.if_index == self.if_index)
		
	def delete(self):
		pass
		
	def get_if_data(self):
		pass
		

