#! /usr/bin/env python

import rospy

import actionlib

from testmsgsrv.msg import *

class FibonacciActioon():

	def __init__(self):
		self._feedback = FibonacciFeedback()
		self._result = FibonacciResult()
		self._as = actionlib.SimpleActionServer('fibonacci', FibonacciAction, execute_cb=self.execute_cb, auto_start = False)
		self._as.start()
	  
	def execute_cb(self, goal):

		r = rospy.Rate(1)
		success = True
		
		
		self._feedback.sequence = [goal.order[0],goal.order[1]]
		
		
		rospy.loginfo('fibonacci: Executing, creating fibonacci sequence of order %i with seeds %i, %i' % (goal.order[2], self._feedback.sequence[0], self._feedback.sequence[1]))
		
	 
		for i in range(1, goal.order[2]):
			if self._as.is_preempt_requested():
				rospy.loginfo('fibonacci: Preempted' )
				self._as.set_preempted()
				success = False
				break
			self._feedback.sequence.append(self._feedback.sequence[i] + self._feedback.sequence[i-1])
			self._as.publish_feedback(self._feedback)
			r.sleep()
		  
		if success:
			self._result.sequence = self._feedback.sequence
			rospy.loginfo('fibonacci: Succeeded')
			self._as.set_succeeded(self._result)
		
if __name__ == '__main__':
	rospy.init_node('fibo_server')
	server = FibonacciActioon()
