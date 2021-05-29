#!/usr/bin/env python

import rospy
from testmsgsrv.srv import *

class MyClass(object):
	def callback(self,msg):
		resp = multimatrixResponse()
		resp.mat3 = "HIIIIIIIII   " + msg.litt1
		return resp
	
	def stt(self):
		rospy.init_node('hello_server')
		s = rospy.Service('helloo', multimatrix, self.callback)
		rospy.spin()
if __name__ == "__main__":
	tt = MyClass()
	tt.stt()