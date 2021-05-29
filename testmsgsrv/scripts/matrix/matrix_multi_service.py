#!/usr/bin/env python

import rospy
import numpy as np
from testmsgsrv.srv import *
from testmsgsrv.msg import *

class MyClass(object):
	def __init__(self):
		pass
	def multiply_matrix(self,req):
		goo = 1
		resp = multimatrixResponse()
		l1 = eval(req.litt1)
		s1 = eval(req.shape1)
		l2 = eval(req.litt2)
		s2 = eval(req.shape2)
		try:
			list_mat1 = []
			list_mat2 = []
			for i in range(s1[0]):
				list_mat1.append([])
			for j in range(s2[0]):
				list_mat2.append([])
			qwe = 0
			aa = 1
			for k in l1:
				list_mat1[qwe].append(k)
				if aa%s1[1] == 0:
				   qwe+=1
				aa+=1
			qwe = 0
			aa = 1
			for m in l2:
				list_mat2[qwe].append(m)
				if aa%s2[1] == 0:
				   qwe+=1
				aa+=1
		except Exception:
			resp.mat3 = "Ooo Engineer.... no. of elements and shape do not match"
			goo = 0
		moasg = matlist()
		moasg.moseg1 = str(list_mat1)
		moasg.moseg2 = str(list_mat2)
		self.pub.publish(moasg)
		try:
			mat1 = np.array(list_mat1)
			mat2 = np.array(list_mat2)
			resp.mat3 = str(np.dot(mat1,mat2))
		except Exception:
			if goo == 1:
				resp.mat3 = "Ooo Engineer.... you can\'t mutiply matrices of these shapes"
		return resp
	def multi_server(self):
		self.pub = rospy.Publisher('/aniket', matlist, queue_size=10)
		rospy.init_node('matrix_multi_service', anonymous=True)
		s = rospy.Service('multiply_matrix', multimatrix, self.multiply_matrix)
		rospy.spin()
if __name__ == "__main__":
	tt = MyClass()
	tt.multi_server()
