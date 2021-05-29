#!/usr/bin/env python

import rospy
from testmsgsrv.srv import *
from testmsgsrv.msg import *

class MyClass(object):
	def __init__(self):
		pass
	def add_it(self,req):
		resp = additResponse()
		resp.c = req.a + req.b
		mosag = add()
		mosag.aa1 = str(req.a)
		mosag.aa2 = str(req.b)
		self.pub.publish(mosag)
		return resp
	
	def add_server(self):
		self.pub = rospy.Publisher('/aniket', add, queue_size=10)
		rospy.init_node('addit_service')
		s = rospy.Service('add_it', addit, self.add_it)
		rospy.spin()
if __name__ == "__main__":
	tt = MyClass()
	tt.add_server()