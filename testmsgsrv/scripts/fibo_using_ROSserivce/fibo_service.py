#!/usr/bin/env python

import rospy
from testmsgsrv.srv import *
from testmsgsrv.msg import *
from std_srvs.srv import Empty,EmptyResponse

class MyClass(object):
	def __init__(self):
		self.do_preempt = 0

	def execute(self,req):
		self.resp = FibonacciiResponse()
		feedbackk = fiboo()
		order = list(eval(req.order))

		iterr = order[:-1]
		print("Starting fibonacci series with seeds %i , %i and order %i" % (order[0], order[1], order[-1]))
		feedbackk.sequence = str(iterr)
		self.pub.publish(feedbackk)

		r = rospy.Rate(1)
		i = 0

		while self.do_preempt == 0 and i <= order[-1]:
			iterr.append(iterr[-1] + iterr[-2])
			feedbackk.sequence = str(iterr)
			self.pub.publish(feedbackk)
			i = i + 1

			r.sleep()



		self.resp.sequence = iterr

		if self.do_preempt == 0:
			print('SUCCEDDED')
		else:
			print('PREEMPTED')
			self.do_preempt = 0

		return self.resp
	
	def add_server(self):
		self.pub = rospy.Publisher('/action', fiboo, queue_size=10)
		rospy.init_node('fibo_service')
		s = rospy.Service('get_fibonacci', Fibonaccii, self.execute)
		p = rospy.Service('preempt_fibonacci', Empty, self.callback)
		rospy.spin()

	def callback(self,req):
		resp = EmptyResponse()
		self.do_preempt = 1
		return resp

if __name__ == "__main__":
	tt = MyClass()
	tt.add_server()
