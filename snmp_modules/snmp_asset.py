#!__VENV_PYTHON__


class SNMPSwAsset():
	_cur_num = "1001"
	_slot_count = 7
	
	#ports = []
        
	def __init__(self, snmp_agent, cur_num = None, is_stackable = False, is_chassi = False, is_module = False):
		self.snmp_agent = snmp_agent
		self._cur_num = cur_num if cur_num else self._cur_num
		#self.hostName = snmp_agent._host_name
		self.is_chassi = is_chassi
		self.is_stackable = is_stackable
		self.is_module = is_module

		if is_chassi:
			self.assetType = 'Chassi'
		elif is_module:
			self.assetType = 'Module'
		else:
			self.assetType = 'Switch'

	def get_serial_num(self):
		physicalSerialNum = '1.3.6.1.2.1.47.1.1.1.1.11'
		nphysicalSerialNum = '1.3.6.1.2.1.47.1.1.1.1.11' + '.' + self._cur_num
		result = self.snmp_agent.snmpGet(nphysicalSerialNum) 
		if result[nphysicalSerialNum] == 'No Such Instance currently exists at this OID':
			self._cur_num = str(1)
			nphysicalSerialNum = '1.3.6.1.2.1.47.1.1.1.1.11' + '.' + self._cur_num
			result = self.snmp_agent.snmpGet(nphysicalSerialNum) 
		return result[nphysicalSerialNum]

	def get_model_name(self):
		physicalModelName = '1.3.6.1.2.1.47.1.1.1.1.13'
		nPhysicalModelName = physicalModelName + '.' + self._cur_num # join .1 or .1001, .2001 ...
		result = self.snmp_agent.snmpGet(nPhysicalModelName )
		if result[nPhysicalModelName] == 'No Such Instance currently exists at this OID':
			self._cur_num = str(1)
			nPhysicalModelName = physicalModelName + '.' + self._cur_num
			result = self.snmp_agent.snmpGet(nPhysicalModelName)
		return result[nPhysicalModelName]

	def get_firmware(self):
		probeDownloadFile = '1.3.6.1.2.1.16.19.6.0'
		result = self.snmp_agent.snmpGet(probeDownloadFile)
		fileName = result[probeDownloadFile].split('/')[-1]
		fileName = fileName.split(':')[-1] if fileName.startswith('flash') or fileName.startswith('sup') or fileName.startswith('boot') else fileName
		return fileName
		
	def get_type(self):
		return self.assetType
	
	def get_ifIndexes(self):
		'''
		Get all interfaces indexes from device
		
		Args:
			snmpAgent(class instance SNMPAgent)
		Returns:
			list: content interface indexes
		'''
		
		ifIndex = '1.3.6.1.2.1.2.2.1.1'
		return [i.split('.')[-1] for i in self.snmp_agent.snmpWalk(ifIndex)]

	def is_a_stackable(self):
		'''
		Checks, if the device has stack ports
		
		Args:
			snmpAgent(class instance SNMPAgent)
		Returns:
			bool:  
		'''
		
		cswRingRedundant = '1.3.6.1.4.1.9.9.500.1.1.3.0' # is stackable
		result = self.snmp_agent.snmpGet(cswRingRedundant)
		return result[cswRingRedundant] != 'No Such Object currently exists at this OID'#return True or False

	def is_a_chassi(self, slot_num = '1000'):
		'''
		Are there any modules ?
		
		Args:
			class instance SNMPAgent: snmpAgent
			str: Slot number
		Returns:
			bool:  
		'''    
		physicalModelName = '1.3.6.1.2.1.47.1.1.1.1.13.' + slot_num # Are there any modules ?
		result = self.snmp_agent.snmpGet(physicalModelName)
		return result[physicalModelName] != 'No Such Instance currently exists at this OID'#return True or False

	def slot_is_busy(self, slot_num):
		return self.is_a_chassi(slot_num = slot_num)
		 
	def get_switch_nums(self):
		'''
		Return list numbers switches in the stack
		
		Args:
			snmpAgent(class instance SNMPAgent)
		Returns:
			list: numbers devices on the stack  
		'''  
		cswSwitchNumCurrent = '1.3.6.1.4.1.9.9.500.1.2.1.1.1'
		result = self.snmp_agent.snmpWalk(cswSwitchNumCurrent)
		return [oid.split('.')[-1] for oid in result]#len(snmpAgent.snmpWalk(cswSwitchNumCurrent))

	def get_ifIndex_neighbor(self):
		'''
		Get interface indexes and number neighbor for which interface there are neighbors
		
		Args:
			snmpAgent(class instance SNMPAgent)
		Returns:
			list dicts: [{ifindex:neighbor_num},]  
		''' 
			
		cdpCacheDeviceId = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'
		result = self.snmp_agent.snmpWalk(cdpCacheDeviceId)
		return [{'ifindex': k.split('.')[-2], 'neighbor_num' : k.split('.')[-1]} for k in result.keys()]

    
    
        
    
 