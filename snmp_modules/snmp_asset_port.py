#!__VENV_PYTHON__

import re
#from snmp_agent import SNMPAgent



class SNMPCDPAssetNeighbor():

	def __init__(self, snmpAgent, ifindex, neighbor_num):
		self.snmpAgent = snmpAgent
		self.ifindex = ifindex
		self.neighbor_num = neighbor_num

	def get_neighbor_ip(self):
		cdpCacheAddress = '1.3.6.1.4.1.9.9.23.1.2.1.1.4' + '.' + self.ifindex + '.' + self.neighbor_num
		result = self.snmpAgent.snmpGet(cdpCacheAddress)
		hexIP = result[cdpCacheAddress]
		return  '.'.join([str(int(hexIP[i:i+2], 16)) for i in range(2, 10, 2)]) if hexIP else None

	def get_neighbor_host_name(self):
		cdpCacheDeviceId = '1.3.6.1.4.1.9.9.23.1.2.1.1.6' + '.' + self.ifindex + '.' + self.neighbor_num
		result = self.snmpAgent.snmpGet(cdpCacheDeviceId)
		nHostName = (result[cdpCacheDeviceId]).replace('.elem.ru', '')
		return nHostName

	def get_neighbor_platform(self):
		cdpCachePlatform = '1.3.6.1.4.1.9.9.23.1.2.1.1.8' + '.' + self.ifindex + '.' + self.neighbor_num
		result = self.snmpAgent.snmpGet(cdpCachePlatform)
		return result[cdpCachePlatform]

	def get_local_ifindex(self):
		return self.ifindex

	def get_neighbor_ifName(self):
		cdpCacheDevicePort  = '.1.3.6.1.4.1.9.9.23.1.2.1.1.7' + '.' + self.ifindex + '.' + self.neighbor_num
		result = self.snmpAgent.snmpGet(cdpCacheDevicePort)
		return result[cdpCacheDevicePort]

	def get_local_ifName(self):
		ifDescr = '1.3.6.1.2.1.2.2.1.2' + '.' + self.ifindex
		result = self.snmpAgent.snmpGet(ifDescr)
		return result[ifDescr]


class SNMPAssetPort():

	#ifStatus = None
	#ifMode = None
	#vlan = 1
	#cdpNeighBor = None
	edgeNeighbor = []

	ifStatusOpt = {'1':'UP',
				   '2':'DOWN',
				   '3':'TESTING'}

	ifModeOpt = {'1':'TRUNK', '2':'ACCESS', '3':'ROUTE'}

	def __init__(self, snmpAgent, portIndex):
		self.snmpAgent = snmpAgent
		self.portIndex = portIndex

	def getIfDescr(self):
		ifDescr = '1.3.6.1.2.1.2.2.1.2' + '.' + self.portIndex
		return (self.snmpAgent.snmpGet(ifDescr))[ifDescr]

	def getIfAStatus(self): 
		ifAdminStatus = '1.3.6.1.2.1.2.2.1.7' + '.' + self.portIndex
		return self.ifStatus[self.snmpAgent.snmpGet(ifAdminStatus)[ifAdminStatus]]

	def getIfOStatus(self):
		ifOperStatus = '1.3.6.1.2.1.2.2.1.8' + '.' + self.portIndex
		return self.snmpAgent.snmpGet(ifOperStatus)[ifOperStatus]

	def getIfAlias(self):
		ifAlias = '1.3.6.1.2.1.31.1.1.1.18' + '.' + self.portIndex
		return self.snmpAgent.snmpGet(ifAlias)[ifAlias]

	def getIfInOctets(self):
		ifInOctets = '1.3.6.1.2.1.2.2.1.10' + '.' + self.portIndex
		return self.snmpAgent.snmpGet(ifInOctets)[ifInOctets]

	def getIfOutOctets(self):
		ifOutOctets = '1.3.6.1.2.1.2.2.1.16' + '.' + self.portIndex
		return self.snmpAgent.snmpGet(ifOutOctets)[ifOutOctets]

	def haveACDPNaighbor(self):
		cdpCacheDeviceId = '1.3.6.1.4.1.9.9.23.1.2.1.1.6' + '.' + self.portIndex
		result = self.snmpAgent.snmpWalk(cdpCacheDeviceId)
		if len(result) == 0:
			return False
		
		self.cdpNeighBor = SNMPCDPAssetNeighbor(self.snmpAgent, self.portIndex, (result[cdpCacheDeviceId].split('.'))[-1])
		return True
    
	def checkIfStatus(self):
		self.ifStatus = self.ifStatusOpt[self.getIfOStatus()]

	def checkIfMode(self):
		vlanTrunkPortDynamicStatus = '1.3.6.1.4.1.9.9.46.1.6.1.1.14' + '.' + self.portIndex
		result = self.snmpAgent.snmpGet(vlanTrunkPortDynamicStatus)
		if result[vlanTrunkPortDynamicStatus] == 'No Such Instance currently exists at this OID':
			result[vlanTrunkPortDynamicStatus] = '3'

		self.ifMode = self.ifModeOpt[result[vlanTrunkPortDynamicStatus]]
    
	def ifVlMapping(self):
		vmVlan = '1.3.6.1.4.1.9.9.68.1.2.2.1.2' + '.' + self.portIndex
		self.vlan = (self.snmpAgent.snmpGet(vmVlan))[vmVlan]



class SNMPAccetPorts():
	ifIndex = '1.3.6.1.2.1.2.2.1.1'
	ifDescr = '1.3.6.1.2.1.2.2.1.2' 							 #+ '.' + portIndex
	ifAlias = '1.3.6.1.2.1.31.1.1.1.18'							 #+ '.' + portIndex
	ifAdminStatus = '1.3.6.1.2.1.2.2.1.7'						 #+ '.' + portIndex
	ifOperStatus = '1.3.6.1.2.1.2.2.1.8' 						 #+ '.' + portIndex
	vlanTrunkPortDynamicStatus = '1.3.6.1.4.1.9.9.46.1.6.1.1.14' #+ '.' + portIndex
	vmVlan = '1.3.6.1.4.1.9.9.68.1.2.2.1.2' 					 #+ '.' + portIndex

	ifName = {'FastEthernet':1, 
			  'GigabitEthernet':1, 
			  'TenGigabitEthernet':1}

	def __init__(self, snmpAgent):
		self.ports = {}
		self.snmpAgent = snmpAgent
		
		rIfIndex = snmpAgent.snmpWalk(self.ifIndex)
		rIfDescr = snmpAgent.snmpWalk(self.ifDescr)
		rIfAlias = snmpAgent.snmpWalk(self.ifAlias)
		rIfAStatus = snmpAgent.snmpWalk(self.ifAdminStatus)
		rIfOStatus = snmpAgent.snmpWalk(self.ifOperStatus)
		rIfMode = snmpAgent.snmpWalk(self.vlanTrunkPortDynamicStatus)
		rVmVlan = snmpAgent.snmpWalk(self.vmVlan)
		
		for r in rIfIndex:
			portIndex = rIfIndex[r]
			nIfDescr = self.ifDescr + '.' + portIndex
			nIfAlias = self.ifAlias + '.' + portIndex
			nVlanTrunkPortDynamicStatus = self.vlanTrunkPortDynamicStatus + '.' + portIndex
			nIfAdminStatus = self.ifAdminStatus + '.' + portIndex
			nIfOperStatus = self.ifOperStatus + '.' + portIndex
			nVmVlan = self.vmVlan + '.' + portIndex

			portDescr = ''.join([s for s in rIfDescr[nIfDescr] if s.isalpha()])
			if not portDescr in self.ifName: 
				continue

			IfMode = rIfMode.get(nVlanTrunkPortDynamicStatus, str(3))
			port = SNMPAssetPort(snmpAgent, portIndex)
			port.ifDescr = rIfDescr[nIfDescr]
			port.ifAlias = rIfAlias [nIfAlias] 
			port.ifAStatus = rIfAStatus[nIfAdminStatus]
			port.ifOStatus = port.ifStatusOpt[rIfOStatus[nIfOperStatus]]
			port.ifMode = port.ifModeOpt[IfMode]
			port.vlan = rVmVlan.get(nVmVlan, 1)
			#if port.ifMode == 'ACCESS' and port.ifOStatus == 'UP':
				


			self.ports.update({portIndex:port})
        
	def get_port_count(self):
		return len(self.ports)
		
	def get_ports(self):
		return self.ports.values()
    
	def lear_edge_neighbor(self):
		'''Getting MAC addresses on access ports'''
		dot1dBasePortIfIndex = '1.3.6.1.2.1.17.1.4.1.2' #Get the port index of whis Vlan
		dot1dTpFdbAddress = '1.3.6.1.2.1.17.4.3.1.1' # For each VLAN, get the MAC address table (using community string indexing Exampe: community@vlanNum(public@1))
		dot1dTpFdbPort = '1.3.6.1.2.1.17.4.3.1.2' # For each VLAN, get the bridge port number (portIndex) (using community string indexing Exampe: community@vlanNum(public@1))
		assetPorts = {}
		for port in self.ports.values():
			if port.vlan not in accessPorts:
				accessPorts[port.vlan] = [port.portIndex]
			else:
				assetPorts[port.vlan].append(port.portIndex)

				community = self.snmpAgent._community

			for vl in assetPorts:
				self.snmpAgent._community = community + '@' + vl # Create indexing community string. Example: public@10
				pIndex = self.snmpAgent.snmpWalk(dot1dBasePortIfIndex) # Getting an dot1dBasePortIfIndex+bridg:index of ports located in this VLAN
				vlCAM =  self.snmpAgent.snmpWalk(dot1dTpFdbAddress) # Get the MAC address table in this VLAN (dot1dTpFdbAddress+address:mac)
				vlBridg = SNMPAccetPorts._invetItems(self.snmpAgent.snmpWalk(dot1dTpFdbPort)) # Get bridg:[dot1dTpFdbPort+address]
				for vlB in vlBridg:
					if dot1dBasePortIfIndex + '.' + vlB not in pIndex:
						pIndex[dot1dBasePortIfIndex + '.' + vlB] = '0' # Vlan 0 imposibl. Continue...

					portIndex = pIndex[dot1dBasePortIfIndex + '.' + vlB]
					if portIndex not in assetPorts[vl]:
						continue
					else:
						macAdd = []
						for o in vlBridg[vlB]:
							macAdd.append((vlCAM[re.sub(dot1dTpFdbPort, dot1dTpFdbAddress, o)]).replace('0x',''))
						self.ports[portIndex].edgeNeighbor = macAdd

			self.snmpAgent._community = community

	def _invetItems(items):
		invertItems = {}
		for i in items:
			if items[i] not in invertItems:
				invertItems[items[i]] = [i]
			else:
				invertItems[items[i]].append(i)
		return invertItems           

	#def get_device_ports(self, curNum='0'):
    #    return {index:port for index,port in self.ports.items() if port.ifDescr.split('/')[0][-1] == curNum}
    




        
