#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import math

key_mapping = {'w':[0,1],'x':[0,-1],
               'a':[-1,0],'d':[1,0],
               's':[0,0]}

g_twist_pub = None
g_target_twist=  None
g_last_twist = None
g_last_send_time =None
g_vel_scales=[0.1,0.1]
g_vel_ramps=[1,1]

def ramp(v_prev,v_target,t_prev,t_now,ramp_rate):
    sign=0
    if v_target > v_prev:
        sign=1
    else:
        sign=-1
    step = ramp_rate*((t_now-t_prev).to_sec())

    if(math.fabs(v_prev-v_target)<step):
        return v_target
    else:
        return v_prev+sign*step

def ramped_twist(prev:Twist,target:Twist,t_prev,t_now,ramps):
    tw = Twist()
    tw.angular.z = ramp(prev.angular.z,target.angular.z,t_prev,t_now,ramps[0])
    tw.linear.x = ramp(prev.linear.x,target.linear.x,t_prev,t_now,ramps[1])
    return tw

def send_twist():
    global g_twist_pub,g_target_twist,g_last_twist,g_last_send_time \
    ,g_vel_scales,g_vel_ramps

    t_now = rospy.Time.now()

    g_last_twist = ramped_twist(g_last_twist,g_target_twist,g_last_send_time,t_now,g_vel_ramps)
    g_last_send_time = t_now
    g_twist_pub.publish(g_last_twist)

def fetchParam(name,default):
    if rospy.has_param(name):
        return rospy.get_param(name)
    else:
        return default



def keys_cb(msg,twist_pub):
     
    global g_target_twist,g_vel_scales


    if len(msg.data) == 0 or not key_mapping.__contains__(msg.data[0]):
        return
    
    vels = key_mapping[msg.data[0]]
    g_target_twist.angular.z = vels[0]*g_vel_scales[0]
    g_target_twist.linear.x = vels[1]*g_vel_scales[1]


g_target_twist =Twist()
g_last_twist = Twist()

rospy.init_node('keys_to_twist')
g_twist_pub = rospy.Publisher('cmd_vel',Twist,queue_size=1)
rospy.Subscriber('keys',String,keys_cb,g_twist_pub)
rate = rospy.Rate(10)
g_last_twist = Twist()
g_last_send_time = rospy.Time.now()
g_vel_scales[0] = fetchParam('~angular_scale',0.1)
g_vel_scales[1] = fetchParam('~linear_scale',0.1)
g_vel_ramps[0] = fetchParam('~angular_accel',1.0)
g_vel_ramps[1] = fetchParam('~linear_accel',1.0)



while not rospy.is_shutdown():
    send_twist()
    rate.sleep()