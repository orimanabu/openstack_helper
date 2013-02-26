#!/usr/bin/env python
# vi: set et sts=4 sw=4 ts=4 :

import gdbm
from pprint import pprint
import sqlalchemy
import sys
import re

dbfile = "test.db"
Tenants = {}
#Networks = {}
Ports = {}

conn_info = {
    'keystone': {'user': 'keystone', 'password': 'keystone', 'host': 'localhost', 'db': 'keystone'},
    'nova': {'user': 'nova', 'password': 'nova', 'host': 'localhost', 'db': 'nova'},
    'quantum': {'user': 'quantum', 'password': 'quantum', 'host': 'localhost', 'db': 'ovs_quantum'}
}

def rdbms_open(service):
    engine = sqlalchemy.create_engine("mysql://%s:%s@%s/%s" % (conn_info[service]['user'], conn_info[service]['password'], conn_info[service]['host'], conn_info[service]['db']))
    #engine.echo = True
    return engine
    
def rdbms_get_tables(conn):
    s = sqlalchemy.sql.text("show tables;")
    return [x[0] for x in conn.execute(s)]

def rdbms_get_table(engine, table_name):
    metadata = sqlalchemy.MetaData(bind=engine)
    table = sqlalchemy.Table(table_name, metadata, autoload=True)
    return table

def table_get_columns(table):
    return [x for x in table.columns.keys()]

def table_get_tmp(table):
    sql = sqlalchemy.sql.select([table])
    res = sql.execute()
    return [x for x in res]
    
def idh_setup():
    db = gdbm.open(dbfile, 'c')
    array = ['aaa', 'bbb', 'ccc', 'ddd', 'eee', 'fff', 'ggg']
    for i, item in enumerate(array):
        db[item] = str(i)
    db.close

def idh_read():
    db = gdbm.open(dbfile)
    k = db.firstkey()
    while k != None:
        print db[k]
        k = db.nextkey(k)

def tenant_setup():
    engine = rdbms_open("keystone")
    table = rdbms_get_table(engine, "tenant")
    keys = table.columns.keys()
    #print "**", keys
    sql = sqlalchemy.sql.select([table])
    #res = sql.execute()
    #print "**", [x for x in res]
    res = sql.execute()
    tenant_info = [dict(zip(keys, a)) for a in [x for x in res]]
    global Tenants
    for ti in tenant_info:
        Tenants[ti['id']] = ti['name']
    return Tenants

def merge_dict(da, db):
    for key in da.keys():
        db[key] = da[key]

#def network_setup0():
#    engine = rdbms_open("quantum")
#    table = rdbms_get_table(engine, "networks")
#    sql = sqlalchemy.sql.select([table.c.id, table.c.name, table.c.tenant_id])
#    array = [dict(zip(('id', 'name', 'tenant'), row)) for row in sql.execute()]
#    global Tenants
#    table = rdbms_get_table(engine, "ovs_network_bindings")
#    for a in array:
#        a['tenant'] = Tenants[a['tenant']]
#        sql = sqlalchemy.sql.select([table.c.network_type, table.c.physical_network, table.c.segmentation_id], table.c.network_id == a['id'])
#        res = sql.execute()
#        row = res.fetchone()
#        a['network_type'] = row[0]
#        a['physical_network'] = row[1]
#        a['segmentation_id'] = row[2]
#    return array
#
## select networks.id as network_id, networks.name as network_name, networks.tenant_id,
##        ovs_network_bindings.physical_network, ovs_network_bindings.segmentation_id,
##        subnets.id as subnet_id, subnets.name as subnet_name, subnets.cidr, subnets.gateway_ip, subnets.enable_dhcp, subnets.shared
## from networks, ovs_network_bindings, subnets
## where networks.id = ovs_network_bindings.network_id
##   and subnets.network_id = networks.id;
#def network_setup():
#    engine = rdbms_open("quantum")
#    networks = rdbms_get_table(engine, "networks")
#    ovs_network_bindings = rdbms_get_table(engine, "ovs_network_bindings")
#    subnets = rdbms_get_table(engine, "subnets")
#    sql = sqlalchemy.sql.select([networks.c.id.label("network_id"), networks.c.name.label("network_name"), networks.c.tenant_id,
#                                 ovs_network_bindings.c.physical_network, ovs_network_bindings.c.segmentation_id,
#                                 subnets.c.id.label("subnet_id"), subnets.c.name.label("subnet_name"), subnets.c.cidr, subnets.c.gateway_ip, subnets.c.enable_dhcp, subnets.c.shared],
#                                 sqlalchemy.sql.and_(networks.c.id == ovs_network_bindings.c.network_id, networks.c.id == subnets.c.network_id))
#    res = sql.execute()
#    array = []
#    dict = {}
#    global Tenants
#    for row in res:
#        #x = {"network_id": row[0],
#        #     "network_name": row[1],
#        #     "tenant": Tenants[row[2]],
#        #     "physical_network": row[3],
#        #     "segmentation_id": row[4],
#        #     "subnet_id": row[5],
#        #     "subnet_name": row[6],
#        #     "cidr": row[7],
#        #     "gateway_ip": row[8],
#        #     "enable_dhcp": row[9],
#        #     "shared": row[10]}
#        #array.append(x)
#        dict[row[0]] = {
#            "network_id": row[0],
#            "network_name": row[1],
#            "tenant": Tenants[row[2]],
#            "physical_network": row[3],
#            "segmentation_id": row[4],
#            "subnet_id": row[5],
#            "subnet_name": row[6],
#            "cidr": row[7],
#            "gateway_ip": row[8],
#            "enable_dhcp": row[9],
#            "shared": row[10]
#        }
#    #return array
#    return dict

# select ports.tenant_id, ports.id as port_id, ports.name as port_name,
#        networks.name as network_name,
#        ports.mac_address, ports.status, ports.device_id, ports.device_owner,
#        ipallocations.ip_address
#   from ports, networks, ipallocations
#  where networks.id = ports.network_id
#    and ports.id = ipallocations.port_id;
def port_setup():
    engine = rdbms_open("quantum")
    networks = rdbms_get_table(engine, "networks")
    ports = rdbms_get_table(engine, "ports")
    ipallocations = rdbms_get_table(engine, "ipallocations")
    sql = sqlalchemy.sql.select([ports.c.tenant_id, ports.c.id.label("port_id"),
                                 networks.c.id.label("network_id"), networks.c.name.label("network_name"),
                                 ports.c.mac_address, ports.c.status, ports.c.device_id, ports.c.device_owner,
                                 ipallocations.c.ip_address],
                                 sqlalchemy.sql.and_(networks.c.id == ports.c.network_id, ports.c.id == ipallocations.c.port_id))
    res = sql.execute()
    dict = {}
    global Tenants
    global Networks
    for row in res:
        elem = {
                    "tenant": Tenants[row[0]] if row[0] else "",
                    "port_id": row[1],
                    "network_id": row[2],
                    "network_name": row[3],
                    #"network": Networks[row[2]],
                    "mac_address": row[4],
                    "status": row[5],
                    "device_id": row[6],
                    "device_owner": row[7],
                    "ip_address": row[8],
        }
        dict[row[1]] = elem
        #if not Networks[row[2]].get("ports"): Networks[row[2]]["ports"] = []
        #Networks[row[2]]["ports"].append(elem)
    return dict

def ipaddr_setup():
    engine = rdbms_open("quantum")
    networks = rdbms_get_table(engine, "networks")
    ports = rdbms_get_table(engine, "ports")
    sql = sqlalchemy.sql.select([ports.c.tenant_id, ports.c.id.label("port_id"),
                                 networks.c.id.label("network_id"), networks.c.name.label("network_name"),
                                 ports.c.mac_address, ports.c.status, ports.c.device_id, ports.c.device_owner],
                                 sqlalchemy.sql.and_(networks.c.id == ports.c.network_id))

def id2name(service, table_name):
    engine = rdbms_open(service)
    table = rdbms_get_table(engine, table_name)
    return [dict(zip(('id', 'name'), row)) for row in sqlalchemy.sql.select([table.c.id, table.c.name]).execute()]

def walk_all():
    for service in conn_info.keys():
        print "=>", service
        engine = rdbms_open(service)
        tables = rdbms_get_tables(engine)
        for table_name in tables:
            print "==>", table_name
            table = rdbms_get_table(engine, table_name)
            array = table_get_columns(table)
            print array
            print table_get_tmp(table)

def filter():
    for line in sys.stdin:
        line = re.sub(r"tap", "tap-", line)
        for port_id in Ports.keys():
            rx = port_id[0:11]
            #print "(%s)" % rx
            #replace = "net:%s,ipaddr:%s,tenant:%s" % (Ports[port_id]["network"]["network_name"], Ports[port_id]["ip_address"], Ports[port_id]["tenant"])
            replace = "net:%s,ipaddr:%s,tenant:%s,owner:%s" % (Ports[port_id]["network_name"], Ports[port_id]["ip_address"], Ports[port_id]["tenant"], Ports[port_id]["device_owner"])
            line = re.sub(rx, replace, line)
        print line,

if __name__ == '__main__':
    Tenants = tenant_setup()
    #Networks = network_setup()
    Ports = port_setup()
    #print "=> tenant"
    #pprint(Tenants)
    #print "=> networks"
    #pprint(Networks)
    #print "=> ports"
    #pprint(Ports)
    filter()
