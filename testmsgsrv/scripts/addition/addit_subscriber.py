#!/usr/bin/env python

import rospy
from testmsgsrv.msg import *

class MyClass(object):
	def __init__(self):
		pass
	def callback(self,msg):
		aa1 = int(float(msg.aa1))
		aa2 = int(float(msg.aa2))
		print("multiplication is ",aa1 * aa2)
	
	def add_server(self):
		pub = rospy.Subscriber('/aniket', add, self.callback)
		rospy.init_node('addit_subscriber')
		rospy.spin()
if __name__ == "__main__":
	tt = MyClass()
	tt.add_server()
