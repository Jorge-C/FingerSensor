#! /usr/bin/env python
from __future__ import division, print_function, absolute_import

from math import copysign

import numpy as np

import rospy
from std_msgs.msg import Int32MultiArray, Header
from geometry_msgs.msg import Vector3, Vector3Stamped

from pap.robot import Baxter
from pap.manager import PickAndPlaceNode


class SmartBaxter(Baxter):
    def __init__(self, limb_name, topic='/sensor_values'):
        super(SmartBaxter, self).__init__(limb_name)
        self.inside = np.zeros(14)
        self.tip = np.zeros(2)
        self.inside_offset = np.zeros_like(self.inside)
        self.tip_offset = np.zeros_like(self.tip)

        self.sensor_sub = rospy.Subscriber(topic,
                                           Int32MultiArray,
                                           self.update_sensor_values,
                                           queue_size=1)
        self.zero_sensor()

    def update_sensor_values(self, msg):
        values = np.array(msg.data)
        self.inside = np.concatenate((values[:7],
                                      values[8:15])) - self.inside_offset
        self.tip = values[[7, 15]] - self.tip_offset
        self.error = np.mean(self.inside[:7] - self.inside[7:])

    def zero_sensor(self):
        rospy.loginfo("Zeroing sensor...")
        inside_vals, tip_vals = [], []
        r = rospy.Rate(10)
        while not rospy.is_shutdown() and len(inside_vals) < 10:
            inside_vals.append(self.inside)
            tip_vals.append(self.tip)
            r.sleep()
        # Center around 5000, so ranges are similar to when not centering
        self.inside_offset = np.min(inside_vals, axis=0) + 5000
        self.tip_offset = np.min(tip_vals, axis=0) + 5000
        rospy.loginfo("Zeroing finished")

    def pick(self, pose, direction=(0, 0, 1), distance=0.1):
        pregrasp_pose = self.translate(pose, direction, distance)

        self.move_ik(pregrasp_pose)
        rospy.sleep(0.5)
        # We want to block end effector opening so that the next
        # movement happens with the gripper fully opened.
        self.gripper.open(block=True)
        while True:
            rospy.loginfo("Going down to pick")
            if self.tip.max() > 10000:
                break
            else:
                h = Header()
                h.stamp = rospy.Time(0)
                h.frame_id = '{}_gripper'.format(self.limb_name)
                scaled_direction = (di / 100 for di in direction)
                v = Vector3(*scaled_direction)
                v_base = self.tl.transformVector3('base',
                                                  Vector3Stamped(h, v)).vector
                v_cartesian = [v_base.x, v_base.y, v_base.z, 0, 0, 0]
                v_joint = self.compute_joint_velocities(v_cartesian)
                self.limb.set_joint_velocities(v_joint)
        rospy.loginfo('Went down!')
        rospy.sleep(0.5)
        rospy.loginfo('Centering')
        while True:
            err = self.error
            rospy.loginfo("err is {}".format(err))
            if abs(err) < 1000:
                break
            y_v = np.clip(1.0 / 30000.0 * err, -0.08, 0.08)
            rospy.loginfo("y_v = {}".format(y_v))
            v = Vector3(0, y_v, 0)
            h = Header()
            h.stamp = rospy.Time(0)
            h.frame_id = '{}_gripper'.format(self.limb_name)
            v_base = self.tl.transformVector3('base',
                                              Vector3Stamped(h, v)).vector
            v_cartesian = [v_base.x, v_base.y, v_base.z, 0, 0, 0]
            v_joint = self.compute_joint_velocities(v_cartesian)
            self.limb.set_joint_velocities(v_joint)
        rospy.loginfo('Centered')
        # self.move_ik(pose)
        rospy.sleep(0.5)
        self.gripper.close(block=True)
        rospy.sleep(0.5)
        self.move_ik(pregrasp_pose)

    def place(self, pose, direction=(0, 0, 1), distance=0.1):
        preplace_pose = self.translate(pose, direction, distance)
        self.move_ik(preplace_pose)
        rospy.sleep(0.5)
        # Edit this. Idea:
        # 1) Move down (direction) until maybe 1cm above place pose.
        # 2) Figure out whether one tip is closer or the other
        # 3) Move left-right to fix that, until values are similar from both tip sensors
        # 4) When kind of close, stop. Move down the missing cm.
        # 5) Open gripper
        # 6) Go to pregrasp
        self.move_ik(self.translate(pose, direction, 0.01))
        r = rospy.Rate(20)
        done = False
        while not done:
            rospy.loginfo("centering")
            delta = self.tip[0] - self.tip[1]
            if abs(delta) < 2000:
                done = True
            else:
                h = Header()
                h.stamp = rospy.Time.now()
                h.frame_id = '{}_gripper'.format(self.limb_name)
                v = Vector3(0, copysign(0.01, delta), 0)
                v_base = self.tl.transformVector3('base', Vector3Stamped(h, v)).vector
                v_cartesian = [v_base.x, v_base.y, v_base.z, 0, 0, 0]
                v_joint = self.compute_joint_velocities(v_cartesian)
                self.limb.set_joint_velocities(v_joint)
                r.sleep()
        rospy.loginfo("centered")
        rospy.sleep(0.5)
        self.move_ik(pose)
        rospy.sleep(0.5)
        self.gripper.open(block=True)
        rospy.sleep(0.5)
        self.move_ik(preplace_pose)


if __name__ == '__main__':
    n = PickAndPlaceNode('left', SmartBaxter)
    rospy.spin()
