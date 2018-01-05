#coding:utf8

import sys, os, getopt, time, select, subprocess
from threading import Thread
from IPy import IP
import commands

class PingThread(Thread):
    def __init__(self, address, count=1):
        Thread.__init__(self) # initialize thread

        # variables
        self.address = address
        self.count = count
        self.status = -1

    def run(self):
        try:
            # get = subprocess.getoutput("ping {} -c {}".format(self.address, self.count))
            get = commands.getoutput("ping {} -c {}".format(self.address, self.count))
        except OSError:
            print("Cannot execute ping, propably you dont have enough permissions to create process")

        lines = get.split("\n")

        for line in lines:
            # find line where is timing given
            if line.find("icmp_") > -1:
                exp = line.split('=')
                # if response is valid
                if len(exp) == 4:
                    self.status = exp[3].replace(' ms', '')


def get_online_server(ip_prefix, group=255, start=0, stop=254):
    """
    ip_prefix: ipv4前3段"192.168.1"
    """
    online_hosts = list()
    task_list = list()
    group = int(group)
    for i in range(start, stop+1):
        current_ip = "%s.%s" % (ip_prefix, i)
        # print "the current_ip is:",ip_prefix
        ping_task = PingThread(current_ip)
        task_list.append(ping_task)
        ping_task.start()

    for task in task_list:
        task.join()
        if task.status == -1:
            pass
            # print("{} not responing, offline".format(task.address))
        else:
            online_hosts.append(task.address)
            # print("{} response in {} ms".format(task.address, task.status))

    sorted_online_hosts =  sorted(online_hosts, key=lambda s: int(s.split('.')[-1]))
    # check_ip_role_type(sorted_online_hosts)
    # return sorted_online_hosts
    online_host_list = list()
    if len(sorted_online_hosts) < group:
        online_host_list.append(sorted_online_hosts)
    else:
        hosts = list()
        for host in sorted_online_hosts:
            hosts.append(host)
            if len(hosts) == group:
                online_host_list.append(hosts)
                hosts = list()
    # print ("the online_host_list is:",online_host_list)
    return online_host_list

    
if __name__ == "__main__":
    main()
    # online_hosts = get_online_server("192.168.7")
    # print(online_hosts)