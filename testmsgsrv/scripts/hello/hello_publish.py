#!/usr/bin/env python

import rospy
from testmsgsrv.msg import *

class MyClass(object):
	def starttt(self):
		self.pub = rospy.Publisher('/anikett', hello, queue_size=10)
		rospy.init_node('hello_publish')
		self.exe()
	def exe(self):
		hel = hello()
		hel.asdfg = "HELLO WORLD"
		r = rospy.Rate(1)
		while not rospy.is_shutdown():
			self.pub.publish(hel)
			r.sleep()
			  
if __name__ == "__main__":
	tt = MyClass()
	tt.starttt()