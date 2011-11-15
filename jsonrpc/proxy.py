
"""
  Copyright (c) 2007 Jan-Klaas Kollhof

  This file is part of jsonrpc.

  jsonrpc is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation; either version 2.1 of the License, or
  (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this software; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import urllib2
from jsonrpc.json import dumps, loads

DEFAULT_URLLIB2_TIMEOUT = 20

class JSONRPCException(Exception):
    def __init__(self, rpcError):
        super(Exception, self).__init__(self)
        self.error = rpcError

class ServiceProxy(object):
    def __init__(self, serviceURL, serviceName=None, serviceVersion="2.0"):
        self.__serviceURL = serviceURL
        self.__serviceName = serviceName
        self.__serviceVersion = serviceVersion

    def __getattr__(self, name):
        if self.__serviceName != None:
            name = "%s.%s" % (self.__serviceName, name)
        return ServiceProxy(self.__serviceURL, name)

    def __call__(self, *args, **kwargs):
        headers = kwargs.pop('headers', {})
        timeout = kwargs.pop('timeout', DEFAULT_URLLIB2_TIMEOUT)
        params = kwargs if len(kwargs) else args
        postdata = dumps({
            'jsonrpc': self.__serviceVersion,
            "method": self.__serviceName,
            'params': params,
            'id':'jsonrpc'})
        postdata = postdata.encode('utf-8')
        req = urllib2.Request(self.__serviceURL, postdata, headers)
        try:
            respdata = urllib2.urlopen(req, timeout=timeout).read()
        except urllib2.HTTPError as err:
            # try read content
            respdata = err.read()
        except urllib2.URLError as err:
            # return the reason of error
            raise Exception(err.reason[-1])
        resp = loads(respdata)
        if resp['error'] != None:
            raise JSONRPCException(resp['error'])
        else:
            return resp['result']
