from snmp_modules.snmp_agent import SNMPAgent
from snmp_modules.snmp_asset import SNMPSwAsset
from snmp_modules.snmp_asset_port import SNMPCDPAssetNeighbor, SNMPAccetPorts
#from snmp_modules.snmp_auxiliary_modules import *

class SNMPSwObj():
	def __init__(self, ip_address, community='public'):
		#self.snmp_agent = SNMPAgent(ip_address, community=community)
		self.snmp_asset_obj = SNMPSwAsset(SNMPAgent(ip_address, community=community))
	
	def check_host_alife(self):
		return self.snmp_asset_obj.snmp_agent.chek_alife()
	
	def get_host_name(self):
		return self.snmp_asset_obj.snmp_agent._host_name
	
	def get_ip(self):
		return self.snmp_asset_obj.snmp_agent.ip_address
		
	def get_mgmt_data(self):
		return {'host_name': self.get_host_name(),
				'ip_address': self.get_ip()}

	def get_asset_serial_nums(self):
		return [asset_obj.get_serial_num() for asset_obj in self.asset_objs_list]
	
	def connect(self):
		'''
		Return list SNMPSwAsset objs instance
		
		return:
			list objs SNMPSwAsset instance
		'''
		asset_objs_list = []
		
		if self.snmp_asset_obj.is_a_stackable(): #check if there are stack ports
			sw_nums_list = self.snmp_asset_obj.get_switch_nums()
			for sw_num in sw_nums_list:
				asset_obj = SNMPSwAsset(self.snmp_asset_obj.snmp_agent, cur_num=sw_num, is_stackable = True)
				if asset_obj.get_serial_num() != '': #if changed the stack, removing the switch
					asset_objs_list.append(asset_obj)
		else:#if is chassi or switch
			asset_obj = (SNMPSwAsset(self.snmp_asset_obj.snmp_agent, cur_num=str(1), is_chassi = True) 
							if self.snmp_asset_obj.is_a_chassi()
							else SNMPSwAsset(self.snmp_asset_obj.snmp_agent))
			asset_objs_list.extend([asset_obj])
			if asset_obj.is_chassi:
				asset_obj.modules = [SNMPSwAsset(self.snmp_asset_obj.snmp_agent, cur_num=str(i) + '000', is_module=True) 
										for i in range(1, SNMPSwAsset._slot_count + 1) 
											if self.snmp_asset_obj.slot_is_busy(slot_num = str(i) + '000')]
				asset_objs_list.extend(asset_obj.modules)
		
		self.asset_objs_list = asset_objs_list
		
		self.learn_ports()
		
	
	def get_neighbors_mgmt_data(self):
	
		'''
		Get neighbors host management data
		
		return:
			list dicts conteining hosts management data 
		'''
		neighbors_mgmt_data_list = []
		learned_hosts_name = []
		
		ifindexes_dict = self.snmp_asset_obj.get_ifIndex_neighbor()
		for kwargs in ifindexes_dict:
			cdp_neighbot_obj = SNMPCDPAssetNeighbor(self.snmp_asset_obj.snmp_agent, **kwargs)
			cdp_neighbor_host_name = cdp_neighbot_obj.get_neighbor_host_name()
			cdp_neighbor_platform = cdp_neighbot_obj.get_neighbor_platform()
			exclude_platforms_list = [cdp_neighbor_platform.startswith('cisco AIR'), #Cisco Access Point
									  cdp_neighbor_platform.startswith('AIR'), #Cisco Access Point and Wireles controller
									  cdp_neighbor_platform.startswith('N')] #Ubiquity nanostatino
			
			#Exclude access points and duplicate ip neighbors (example Etherchannel interfaces)
			if not any(exclude_platforms_list) and cdp_neighbor_host_name not in learned_hosts_name:
				learned_hosts_name.append(cdp_neighbor_host_name)
				neighbors_mgmt_data_list.append({'host_name': cdp_neighbor_host_name,
												 'ip_address': cdp_neighbot_obj.get_neighbor_ip()})
		
		return neighbors_mgmt_data_list

	def get_inventory_data(self):
		return [{'manufacturer':'Cisco',
				 'model': asset.get_model_name(),
				 'firmware': asset.get_firmware(),
				 'type':asset.get_type(),
				 'serial_num':asset.get_serial_num()} for asset in self.asset_objs_list]
	
	def get_ports_data(self, full=False):
		if full:
			return {port.portIndex:{'if_index':port.portIndex,
									'oper_status': True if port.ifOStatus=='UP' else False,
									'mode': port.ifMode,
									'vlan': port.vlan} for port in self.ports}
		else:
			return {port.portIndex:{'if_index':port.portIndex,
									'if_name': port.ifDescr,
									'description': port.ifAlias,
									'admin_status': True if port.ifAStatus else False, 
									'oper_status': True if port.ifOStatus=='UP' else False,
									'mode': port.ifMode,
									'vlan': port.vlan} for port in self.ports}
								 
	def learn_ports(self):
		self.ports = SNMPAccetPorts(self.snmp_asset_obj.snmp_agent).get_ports()
			  
		
			

		
		