openstack_helper
================

This project contains my private helper scripts for OpenStack, tested with Red Hat OpenStack Folsom Preview.

Osfilter.py is a filter to convert from obscure port names with UUIDs to some more meaningful ones.
For example, in many cases with Quantum, you would see many hard-to-understand port names like this:

	[osuser@folsom-controller openstack_helper]$ sudo ovs-vsctl show
	cced53eb-8cdd-41c0-adcf-560153705733
	    Bridge br-int
		Port br-int
		    Interface br-int
			type: internal
		Port "qr-f56c520c-28"
		    tag: 2
		    Interface "qr-f56c520c-28"
			type: internal
		Port "tapdb594f10-9d"
		    tag: 3
		    Interface "tapdb594f10-9d"
			type: internal
		Port int-br-ex
		    Interface int-br-ex
		Port "qr-9b481baf-f5"
		    tag: 3
		    Interface "qr-9b481baf-f5"
			type: internal
		Port "tapd88154a9-0a"
		    tag: 2
		    Interface "tapd88154a9-0a"
			type: internal
		Port "tap83ab55ad-cb"
		    tag: 1
		    Interface "tap83ab55ad-cb"
			type: internal
		Port "int-br-eth2"
		    Interface "int-br-eth2"
	    Bridge br-ex
		Port phy-br-ex
		    Interface phy-br-ex
		Port "eth3"
		    Interface "eth3"
		Port "qg-d92f6e97-2f"
		    Interface "qg-d92f6e97-2f"
			type: internal
		Port br-ex
		    Interface br-ex
			type: internal
	    Bridge "br-eth2"
		Port "br-eth2"
		    Interface "br-eth2"
			type: internal
		Port "eth2"
		    Interface "eth2"
		Port "phy-br-eth2"
		    Interface "phy-br-eth2"
	    ovs_version: "1.7.1"

With osfilter.py, the output of ovs-vsctl is converted clearer to some degree.

	[osuser@folsom-controller openstack_helper]$ sudo ovs-vsctl show | ./osfilter.py 
	cced53eb-8cdd-41c0-adcf-560153705733
	    Bridge br-int
		Port br-int
		    Interface br-int
			type: internal
		Port "qr-net:test,ipaddr:172.16.200.1,tenant:test,owner:network:router_interface"
		    tag: 2
		    Interface "qr-net:test,ipaddr:172.16.200.1,tenant:test,owner:network:router_interface"
			type: internal
		Port "tap-net:demo,ipaddr:172.16.100.2,tenant:demo,owner:network:dhcp"
		    tag: 3
		    Interface "tap-net:demo,ipaddr:172.16.100.2,tenant:demo,owner:network:dhcp"
			type: internal
		Port int-br-ex
		    Interface int-br-ex
		Port "qr-net:demo,ipaddr:172.16.100.1,tenant:demo,owner:network:router_interface"
		    tag: 3
		    Interface "qr-net:demo,ipaddr:172.16.100.1,tenant:demo,owner:network:router_interface"
			type: internal
		Port "tap-net:test,ipaddr:172.16.200.2,tenant:test,owner:network:dhcp"
		    tag: 2
		    Interface "tap-net:test,ipaddr:172.16.200.2,tenant:test,owner:network:dhcp"
			type: internal
		Port "tap-net:demo2,ipaddr:172.16.110.2,tenant:demo,owner:network:dhcp"
		    tag: 1
		    Interface "tap-net:demo2,ipaddr:172.16.110.2,tenant:demo,owner:network:dhcp"
			type: internal
		Port "int-br-eth2"
		    Interface "int-br-eth2"
	    Bridge br-ex
		Port phy-br-ex
		    Interface phy-br-ex
		Port "eth3"
		    Interface "eth3"
		Port "qg-net:public,ipaddr:192.168.200.2,tenant:,owner:network:router_gateway"
		    Interface "qg-net:public,ipaddr:192.168.200.2,tenant:,owner:network:router_gateway"
			type: internal
		Port br-ex
		    Interface br-ex
			type: internal
	    Bridge "br-eth2"
		Port "br-eth2"
		    Interface "br-eth2"
			type: internal
		Port "eth2"
		    Interface "eth2"
		Port "phy-br-eth2"
		    Interface "phy-br-eth2"
	    ovs_version: "1.7.1"

You can use osfilter.py with any command other than ovs-vsctl, for example ip.

	[osuser@folsom-controller openstack_helper]$ ip link show | grep -v '^ ' | ./osfilter.py 
	1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN 
	2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
	3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
	4: eth2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
	5: eth3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
	6: br-eth2: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN 
	7: br-int: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN 
	8: br-ex: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN 
	9: qr-net:test,ipaddr:172.16.200.1,tenant:test,owner:network:router_interface: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN 
	10: tap-net:test,ipaddr:172.16.200.2,tenant:test,owner:network:dhcp: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN 
	11: qr-net:demo,ipaddr:172.16.100.1,tenant:demo,owner:network:router_interface: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN 
	12: tap-net:demo,ipaddr:172.16.100.2,tenant:demo,owner:network:dhcp: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN 
	13: tap-net:demo2,ipaddr:172.16.110.2,tenant:demo,owner:network:dhcp: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN 
	14: qg-net:public,ipaddr:192.168.200.2,tenant:None,owner:network:router_gateway: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN 
	16: phy-br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
	17: int-br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
	18: phy-br-eth2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
	19: int-br-eth2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000

