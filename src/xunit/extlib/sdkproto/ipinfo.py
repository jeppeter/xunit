#! python

'''
	this is the file for the ipinfo get and set
'''

import struct

import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..')))
import xunit.utils.exception

SYSCODE_GET_IPINFO_REQ=1013
SYSCODE_GET_IPINFO_RSP=1014

SYS_HDR_LENGTH=16
NET_INFO_STRUCT_LENGTH=296
MESSAGE_CODE_LENGTH=8

class SdkIpInfoInvalidError(xunit.utils.exception.XUnitException):
	pass

class SdkIpInfoOutRangeError(xunit.utils.exception.XUnitException):
	pass

class NetInfoInvalidError(xunit.utils.exception.XUnitException):
	pass



class NetInfo:
	def __init__(self):
		self.__netid = -1
		self.__ifname = ''
		self.__ipaddr = ''
		self.__submask = ''
		self.__gateway = ''
		self.__dns = ''
		self.__hwaddr = ''
		self.__dhcp = -1
		return

	def __del__(self):
		self.__netid = -1
		self.__ifname = ''
		self.__ipaddr = ''
		self.__submask = ''
		self.__gateway = ''
		self.__dns = ''
		self.__hwaddr = ''
		self.__dhcp = -1
		return

	def __GetString(self,s,size):
		rbuf = ''
		lasti  = -1
		for i in xrange(size):
			if s[i] == '\0':
				lasti = i
				break

		if lasti >= 0:
			rbuf = s[:lasti]
		else:
			rbuf = s[:-2]
		return rbuf
	def __FormatString(self,s,size):
		rbuf = ''
		if len(s) < size:
			rbuf += s
			lsize = size - len(s)
			rbuf += '\0' * lsize
		else:
			rbuf += s[:(size-1)]
			rbuf += '\0'
		return rbuf
		
	

	def GetNetId(self):
		return self.__netid

	def GetIfName(self):
		return self.__ifname

	def GetIpAddr(self):
		return self.__ipaddr

	def GetSubMask(self):
		return self.__submask

	def GetGateway(self):
		return self.__gateway

	def GetDns(self):
		return self.__dns

	def GetHwAddr(self):
		return self.__hwaddr

	def GetDhcp(self):
		return self.__dhcp

	def SetNetId(self,val):
		ov = self.__netid
		self.__netid = val
		return ov

	def SetIfName(self,val):
		ov = self.__ifname
		self.__ifname = val
		return ov

	def SetIpAddr(self,val):
		ov = self.__ipaddr
		self.__ipaddr = val
		return ov

	def SetSubMask(self,val):
		ov = self.__submask
		self.__submask = ov
		return ov

	def SetGateway(self,val):
		ov = self.__gateway
		self.__gateway = val
		return ov

	def SetDns(self,val):
		ov = self.__dns
		self.__dns = val
		return ov

	def SetHwAddr(self,val):
		ov = self.__hwaddr
		self.__hwaddr =val
		return ov

	def SetDhcp(self,val):
		ov = self.__dhcp
		self.__dhcp = val
		return ov

	def ParseBuffer(self,buf):
		if len(buf) < NET_INFO_STRUCT_LENGTH:
			raise NetInfoInvalidError('len(%d) < (%d)'%(len(buf),NET_INFO_STRUCT_LENGTH))
		self.__netid = struct.unpack('>I',buf[:4])[0]
		self.__ifname = self.__GetString(buf[4:36],32)
		self.__ipaddr = self.__GetString(buf[36:68],32)
		self.__submask = self.__GetString(buf[68:100],32)
		self.__gateway = self.__GetString(buf[100:132],32)
		self.__dns = self.__GetString(buf[132:260],128)
		self.__hwaddr = self.__GetString(buf[260:292],32)
		self.__dhcp = ord(buf[292])
		return

	def FormatBuffer(self):
		rbuf = ''
		rbuf += struct.pack('>I',self.__netid)
		rbuf += self.__FormatString(self.__ifname,32)
		rbuf += self.__FormatString(self.__ipaddr,32)
		rbuf += self.__FormatString(self.__submask,32)
		rbuf += self.__FormatString(self.__gateway,32)
		rbuf += self.__FormatString(self.__dns,128)
		rbuf += self.__FormatString(self.__hwaddr,32)
		rbuf += chr(self.__dhcp)
		rubf += chr(0)
		rubf += chr(0)
		rubf += chr(0)

		return rbuf

class SdkIpInfo:
	def __init__(self):
		self.__seqid = -1
		self.__sesid = -1
		self.__res = -1
		self.__netinfos = []
		return

	def __del__(self):
		self.__seqid = -1
		self.__sesid = -1
		self.__res = -1
		self.__netinfos = []
		return

	def FormatQueryInfo(self,seqid,sesid):
		rbuf = ''
		rbuf += 'GSMT'
		# give the version 1 
		rbuf += chr(1)
		# header length 16
		rbuf += chr(SYS_HDR_LENGTH)
		#code is SYSCODE_GET_IPINFO_REQ
		rbuf += struct.pack('>H',SYSCODE_GET_IPINFO_REQ)
		# attribute is 0
		# seqid sesid and totallength is body length 0
		rbuf += struct.pack('>HHHH',0,seqid,sesid,SYS_HDR_LENGTH)
		return rbuf

	def ParseQueryInfo(self,buf):
		if len(buf) < SYS_HDR_LENGTH:
			raise SdkIpInfoInvalidError('len (%d) < (%d)'%(len(buf),SYS_HDR_LENGTH))
		if buf[:4] != 'GSMT':
			raise SdkIpInfoInvalidError('tag (%s) != (GSMT)'%(repr(buf[:4])))

		if buf[4] != chr(1):
			raise SdkIpInfoInvalidError('version (%d) != 1'%(ord(buf[4])))

		if buf[5] != chr(SYS_HDR_LENGTH):
			raise SdkIpInfoInvalidError('hdrlen (%d) != (%d)'%(ord(buf[5]),SYS_HDR_LENGTH))

		code = struct.unpack('>H',buf[6:8])[0]
		if code != SYSCODE_GET_IPINFO_RSP:
			raise SdkIpInfoInvalidError('code (%d) != (%d)'%(code,SYSCODE_GET_IPINFO_RSP))

		attrcount =struct.unpack('>H',buf[8:10])[0]
		if attrcount < 2:
			raise SdkIpInfoInvalidError('attrcount (%d) < 2'%(attrcount))

		self.__seqid,self.__sesid = struct.unpack('>HH',buf[10:14])
		tlen = struct.unpack('>H',buf[14:16])[0]
		if tlen > len(buf):
			raise SdkIpInfoInvalidError('total length (%d) > (%d)'%(tlen,len(buf)))
		tlen -= SYS_HDR_LENGTH

		attrbuf = buf[SYS_HDR_LENGTH:]
		self.__netinfos = []
		for i in xrange(attrcount):
			mesgbuf = attrbuf[:MESSAGE_CODE_LENGTH]
			res,mlen = struct.unpack('>II',mesgbuf)
			pbuf = attrbuf[MESSAGE_CODE_LENGTH:(mlen+MESSAGE_CODE_LENGTH)]
			attrbuf = attrbuf[(mlen+MESSAGE_CODE_LENGTH):]
			netinfo = NetInfo()
			netinfo.ParseBuffer(pbuf)
			self.__netinfos.append(netinfo)

		
		return len(self.__netinfos)

	def GetSessionId(self):
		return self.__sesid

	def GetSeqId(self):
		return self._seqid

	def GetIpInfo(self,idx):
		if idx >= len(self.__netinfos):
			raise SdkIpInfoOutRangeError('(%d) >= (%d)'%(idx,len(self.__netinfos)))
		return self.__netinfos[idx]