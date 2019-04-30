#!/usr/bin/env python3
import datetime
from snmp_modules import *
from db_modules import *

e=0
community = 'ciscoro'
ip_addresses_list = ['172.30.22.7']#['172.30.22.1', '172.30.76.100', '172.30.146.30', '172.30.4.3', '172.30.131.4', '172.16.5.8', '172.16.5.16']

learned_assets = {}
assets_to_study = []


for ip_address in ip_addresses_list:
		
	if e == -1: #len(ip_addresses_list):
		break
	e+=1
	
	snmp_asset_obj = SNMPSwObj(ip_address, community)
	
	if not snmp_asset_obj.check_host_alife():
		#in future write to error file
		print ('This ip {0} not avalible\n{1}\n'.format(snmp_asset_obj.get_ip(), 
														snmp_asset_obj.snmp_asset_obj.snmp_agent._errorIndication))
		e-=1
		continue
	
	snmp_asset_obj.connect()
	learned_assets.update({snmp_asset_obj.get_host_name():snmp_asset_obj})
	#cdp_neighbors = snmp_asset_obj.get_neighbors_mgmt_data()	
	
	ip_addresses_list.extend([mgmt.get('ip_address') for mgmt in snmp_asset_obj.get_neighbors_mgmt_data()
														#An example distribution switch is learned later by the access switches connected to it.
														#and ip address not previously added														
														if mgmt.get('host_name') not in learned_assets and
														   mgmt.get('ip_address') not in ip_addresses_list])				   
	
	print('{:<4} Learned: {:<25} {:<15}'.format(str(e) + '.', snmp_asset_obj.get_host_name(), snmp_asset_obj.get_ip()))
		
		
db.connect()

for snmp_asset_obj in learned_assets.values():
	asset_mgmt_data = snmp_asset_obj.get_mgmt_data()

	db_asset_obj = DbAssetObj(**asset_mgmt_data)
	if db_asset_obj.in_db:
		if db_asset_obj == snmp_asset_obj:
			asset_data = {'ports':snmp_asset_obj.get_ports_data()}
			db_asset_obj.update(asset_data)
			continue
		else:#
			db_asset_obj.delete()
	
	#else asset not in DB or asset deleted on DB
	asset_data = {'inventory_data':snmp_asset_obj.get_inventory_data(),
				  'ports':snmp_asset_obj.get_ports_data(full=True)}
	db_asset_obj.create(asset_data)


db.close()
