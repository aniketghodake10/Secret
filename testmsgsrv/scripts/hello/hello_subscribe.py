#!/usr/bin/env python

import rospy
from testmsgsrv.msg import *

class MyClass(object):
	def callback(self,msg):
		print(msg.asdfg)
	
	def stt(self):
		pub = rospy.Subscriber('/anikett', hello, self.callback)
		rospy.init_node('hello_subscribe')
		rospy.spin()
if __name__ == "__main__":
	tt = MyClass()
	tt.stt()