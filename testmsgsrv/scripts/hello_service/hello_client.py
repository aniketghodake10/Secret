#!/usr/bin/env python

import sys
import rospy
from testmsgsrv.srv import *

class Myclasss():
	def __init__(self):
		rospy.init_node('hello_client', anonymous=True)

	def babooo(self,x):
		rospy.wait_for_service('helloo')
		try:
			fff = rospy.ServiceProxy('helloo', multimatrix)
			respp = fff(x,x,x,x)
			print("Got the service response = ",respp.mat3)
		except rospy.ServiceException as e:
			print("Service call failed: %s"%e)



if __name__ == "__main__":
	x = sys.argv[1]
	obbject = Myclasss()
	obbject.babooo(x)