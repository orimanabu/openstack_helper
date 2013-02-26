#!/usr/bin/env python
# vi: set et sts=4 sw=4 ts=4 :

import gdbm
from pprint import pprint
import sqlalchemy
import sys
import re

dbfile = "test.db"
Tenants = {}
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
                    "tenant": Tenants[row[0]] if row[0] else "None",
                    "port_id": row[1],
                    "network_id": row[2],
                    "network_name": row[3],
                    "mac_address": row[4],
                    "status": row[5],
                    "device_id": row[6],
                    "device_owner": row[7],
                    "ip_address": row[8],
        }
        dict[row[1]] = elem
    return dict

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
            replace = "net:%s,ipaddr:%s,tenant:%s,owner:%s" % (Ports[port_id]["network_name"], Ports[port_id]["ip_address"], Ports[port_id]["tenant"], Ports[port_id]["device_owner"])
            line = re.sub(rx, replace, line)
        print line,

if __name__ == '__main__':
    Tenants = tenant_setup()
    Ports = port_setup()
    filter()
