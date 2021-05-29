#!/usr/bin/env python

import sys
import rospy
from testmsgsrv.srv import *
from testmsgsrv.msg import *
from std_srvs.srv import Empty,EmptyResponse
from threading import *

class Myclasss():
	def __init__(self):
		rospy.init_node('fibo_client_service', anonymous=True)
		rospy.Subscriber('/action', fiboo, self.callback)

	def babooo(self,x):
		rospy.wait_for_service('get_fibonacci')
		try:
			fff = rospy.ServiceProxy('get_fibonacci', Fibonaccii)
			respp = fff(x)
			print("Final Fibonacci Series = %s"%(str(respp.sequence)))
		except rospy.ServiceException as e:
			print("Service call failed: %s"%e)

	def callback(self,msg):
		print("Feedback : Sequence : ",msg.sequence)
		# if eval(msg.sequence)[-1] == 144:
		# 	print('asdfghjkl')
		# 	self.preempt()

	def preempt(self):
		rospy.wait_for_service('preempt_fibonacci')
		try:
			fff = rospy.ServiceProxy('preempt_fibonacci', Empty)
			respp = fff()
		except rospy.ServiceException as e:
			print("Service call failed: %s"%e)


if __name__ == "__main__":
	x = sys.argv[1]
	obbject = Myclasss()

	t1 = Thread(target=obbject.babooo, args=(x,))
	t1.start()

	print('threading success')
