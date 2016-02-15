import rospy
from sensor_msgs.msg import Imu
from sensor_msgs.msg import JointState
    
def callback(data):
	rospy.loginfo("%s %s", data.header.stamp.nsecs,data.linear_acceleration)

def listener():
	rospy.Subscriber("/robot/accelerometer/left_accelerometer/state", Imu, callback)	

def callback2(data):
	if len(data.effort) == 17: 
		rospy.loginfo("%s %s",data.header.stamp.nsecs, data.effort[15] )

def listener2():
	rospy.Subscriber("/robot/joint_states", JointState, callback2)

rospy.init_node('accel_listener', anonymous=True)
l = listener()
l2 = listener2()
rospy.spin()
