#!/usr/bin/env python

import rospy
from testmsgsrv.msg import *

class MyClass(object):
	def __init__(self):
		pass
	def callback(self,msg):
		aa1 = eval(msg.moseg1)
		aa2 = eval(msg.moseg2)
		print("no. of rows of two matrices are ",len(aa1),"and",len(aa2))
	
	def mat_server(self):
		pub = rospy.Subscriber('/aniket', matlist, self.callback)
		rospy.init_node('matrix_subscriber')
		rospy.spin()
if __name__ == "__main__":
	tt = MyClass()
	tt.mat_server()