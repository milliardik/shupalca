#!__VENV_PYTHON__
from pysnmp.hlapi import *



class SNMPAgent():
    #ip_address = '127.0.0.1'
    
    _port = 161
    _community = 'public'
    
    _host_name = None 
    
    _errorIndication = False
    
    def __init__(self, ip_address, port = None, community = None):
        self.ip_address = ip_address
        if port:
            self._port = port
        if  community:
            self._community = community
        
            
    def snmpWalk(self, oid):
        result = []
        for (errorIndication,
            errorStatus,
            errorIndex,
            varBinds) in nextCmd(SnmpEngine(),
                                 CommunityData(self._community),
                                 UdpTransportTarget((self.ip_address, self._port)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid)),
                                 lexicographicMode  = False,
                                 lookupMib = False):
       
           if errorIndication:
               self._errorIndication = errorIndication
               break
           elif errorStatus:
               print('%s at %s' % (errorStatus.prettyPrint(),
                                   errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
               break
           else:
               for varBind in varBinds:
                   result.append([x.prettyPrint() for x in varBind])#print(' = '.join([x.prettyPrint() for x in varBind]))
        return {r[0]:r[1] for r in result}

    def snmpGet(self, oid):
        result = []
        errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(SnmpEngine(),
                                                                CommunityData(self._community),
                                                                UdpTransportTarget((self.ip_address, self._port)),
                                                                ContextData(),
                                                                ObjectType(ObjectIdentity(oid)),
                                                                lookupMib = False))
    
        if errorIndication:
            self._errorIndication = errorIndication
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                result = ([x.prettyPrint() for x in varBind])
       
        if self._errorIndication:
            result = [oid, '']
        
        return {result[0]:result[1]}

    def chek_alife(self):
        sysName = '1.3.6.1.2.1.1.5.0'
        result = self.snmpGet(sysName) or {}

        if self._errorIndication:
            return False
        else:
            self._host_name = ((result[sysName]).split('.')[0]).replace('.elem.ru','')
            return True
    
    
    
if __name__ == '__main__':
    community  = 'ciscoro'
    ip_addresses= ['172.30.22.10'] #['172.30.22.8', '172.30.22.3', '172.30.255.1', '172.30.132.1', '172.30.67.1', '172.31.255.2', '172.30.76.100', '172.30.22.7']
    
    
    for ip_addres in  ip_addresses:
        agent = SNMPAgent(ip_addres, port=161, community=community)
        if not agent.chek_alife():
            '''Write to error file'''
            print ('This ip {0} not avalible\n{1}\n'.format(agent.ipAddress, agent._errorIndication))
            continue
        else:
            print (agent.snmpWalk('1.3.6.1.4.1.9.9.23.1.2.1.1.6.10101'))