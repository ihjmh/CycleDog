#!/usr/bin/python 
#coding:utf-8 
import socket 
import struct 
import fcntl 
#import cps_config

def getip(ethname):
    s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0X8915, struct.pack('256s', ethname[:15].encode('utf-8')))[20:24]) 

if __name__=='__main__':
	main()