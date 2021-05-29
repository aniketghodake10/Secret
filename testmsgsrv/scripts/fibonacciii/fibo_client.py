#! /usr/bin/env python

import rospy
import sys
import actionlib
from testmsgsrv.msg import *


def fibonacci_client():
	client = actionlib.SimpleActionClient('fibonacci', FibonacciAction)
	client.wait_for_server()

	goal = FibonacciGoal(order=eval(sys.argv[1]))

	client.send_goal(goal,active_cb=callback_active,
					feedback_cb=callback_feedback,
					done_cb=callback_done)
	
def callback_active():
	rospy.loginfo("Action server is processing the goal")

def callback_done(state, result):
	rospy.loginfo("Action server is done. State: %s, result: %s" % (str(state), str(result)))

def callback_feedback(feedback):
	rospy.loginfo("Feedback:%s" % str(feedback))

if __name__ == '__main__':
	rospy.init_node('fibo_client')
	fibonacci_client()
	rospy.spin()
