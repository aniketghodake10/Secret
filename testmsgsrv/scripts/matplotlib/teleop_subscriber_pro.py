#!/usr/bin/env python3
import rospy
import math
import matplotlib.pyplot as plt
from geometry_msgs.msg import Twist
from testmsgsrv.srv import teleop, teleopResponse


def callback(yoo):
	global config,xx,yy
	x11 = yoo.linear.x
	t3 = yoo.angular.z
	
	if x11 == 2 or x11 == -2:
		find_coordinates(x11)

	if t3 == 2:
		print('Rotate left by 10 degrees')
		config = config + 10
		if config == 370:
			config = 10
	if t3 == -2:
		print('Rotate right by 10 degrees')
		config = config - 10
		if config == 0:
			config = 360

class plotit():
	def __init__(self):
		self.letsplot = 0
	def plott(self,req):
		global xx, yy
		resp = teleopResponse()
		self.letsplot = 1

		resp.initial = [0,0]
		resp.destination = [flsr(xx[-1]),flsr(yy[-1])]
		return resp

def resett(req):
	resp = teleopResponse()
	global config,xx,yy
	config = 1
	xx = [0]
	yy = [0]

	resp.initial = [0,0]
	resp.destination = [0,0]
	return resp


def radians(deg):
    return deg * math.pi / 180


def find_coordinates(x11):
	global config, xx, yy

	if x11 == 2:
		print('Move forward by 2 units')
	if x11 == -2:
		print('Move backward by 2 units')

	y0 = yy[-1]
	x0 = xx[-1]

	if 89 >= config >= 1 or 359 >= config >= 271:
		m = math.tan(radians(config))
		c = y0 - m * x0

		x1 = x0 + 2
		y1 = m * x1 + c
		

	if 179 >= config >= 91 or 269 >= config >= 181:
		m = math.tan(radians(config))
		c = y0 - m * x0

		x1 = x0 - 2
		y1 = m * x1 + c

	if config == 90:
		x1 = x0
		y1 = y0 + 2

	if config == 180:
		x1 = x0 - 2
		y1 = y0

	if config == 270:
		x1 = x0
		y1 = y0 - 2

	if config == 360:
		x1 = x0 + 2
		y1 = y0


	d = math.sqrt((y1 - y0)**2 + (x1 - x0)**2)
	t = x11 / d

	xt = (1 - t) * x0 + t * x1
	yt = (1 - t) * y0 + t * y1

	yy.append(flsr(yt))
	xx.append(flsr(xt))


def flsr(a):
    return float('{:.3f}'.format(float(a)))




if __name__ == "__main__":
	config = 90
	xx = [0]
	yy = [0]
	pp = plotit()
	rospy.init_node('teleop_subscriber_pro')
	rospy.Subscriber('/turtle1/cmd_vel',Twist,callback)

	s = rospy.Service('plot_trajectory', teleop, pp.plott)
	ss = rospy.Service('plot_reset', teleop, resett)

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