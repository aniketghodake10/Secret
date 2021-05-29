#!/usr/bin/env python3
import rospy
import matplotlib.pyplot as plt
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty,EmptyResponse


def callback(yoo):
	global config,xx,yy
	x1 = yoo.linear.x
	t3 = yoo.angular.z
	if x1 == 2:
		print('Move forward by 2 units')
		if config == 1:
			addyy = yy[-1]
			addxx = xx[-1]
			yy.append(addyy + 2)
			xx.append(addxx)

		if config == 2:
			addyy = yy[-1]
			addxx = xx[-1]
			yy.append(addyy)
			xx.append(addxx + 2)

		if config == 3:
			addyy = yy[-1]
			addxx = xx[-1]
			yy.append(addyy - 2)
			xx.append(addxx)

		if config == 4:
			addyy = yy[-1]
			addxx = xx[-1]
			yy.append(addyy)
			xx.append(addxx - 2)
	if x1 == -2:
		print('Move backward by 2 units')
		if config == 1:
			addyy = yy[-1]
			addxx = xx[-1]
			yy.append(addyy - 2)
			xx.append(addxx)

		if config == 2:
			addyy = yy[-1]
			addxx = xx[-1]
			yy.append(addyy)
			xx.append(addxx - 2)

		if config == 3:
			addyy = yy[-1]
			addxx = xx[-1]
			yy.append(addyy + 2)
			xx.append(addxx)

		if config == 4:
			addyy = yy[-1]
			addxx = xx[-1]
			yy.append(addyy)
			xx.append(addxx + 2)
	if t3 == 2:
		print('Rotate left by 90 degrees')
		config = config - 1
		if config == 0:
			config = 4
	if t3 == -2:
		print('Rotate right by 90 degrees')
		config = config + 1
		if config == 5:
			config = 1

class plotit():
	def __init__(self):
		self.letsplot = 0
	def plott(self,req):
		resp = EmptyResponse()
		self.letsplot = 1
		return resp

def resett(req):
	resp = EmptyResponse()
	global config,xx,yy
	config = 1
	xx = [0]
	yy = [0]
	return resp


if __name__ == "__main__":
	config = 1
	xx = [0]
	yy = [0]
	pp = plotit()
	rospy.init_node('teleop_subscriber')
	rospy.Subscriber('/turtle1/cmd_vel',Twist,callback)

	s = rospy.Service('plot_trajectory', Empty, pp.plott)
	ss = rospy.Service('plot_reset', Empty, resett)

	plt.style.use('dark_background')
	plt.plot(xx,yy,'b*')
	plt.show() 
	
	while not rospy.is_shutdown():
		if pp.letsplot == 1:
			pp.letsplot = 0
			plt.style.use('dark_background')
			plt.plot(xx,yy)
			plt.plot(xx[0],yy[0],'b*')
			plt.plot(xx[-1],yy[-1],'r*')
			plt.show()