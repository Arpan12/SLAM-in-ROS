

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


def scan_callback(msg):
    range_ahead = msg.ranges[int(len(msg.ranges)/2)]
    print(f"range ahead: {range_ahead}")


cmd_vel_pub = rospy.Publisher('cmd_vel',Twist,queue_size=1)
scan_sub = rospy.Subscriber('scan',LaserScan,scan_callback)
rospy.init_node('red_light_green_light')

red_light_Twist = Twist()
green_light_Twist = Twist()
green_light_Twist.linear.x = 0.5

driving_forward = True
change_light = rospy.Time.now()
rate = rospy.Rate(10)


while True:
    if driving_forward:
        cmd_vel_pub.publish(green_light_Twist)
    else:
        cmd_vel_pub.publish(red_light_Twist)
    
    if change_light < rospy.Time.now():
        driving_forward  = not driving_forward
        change_light = rospy.Time.now() + rospy.Duration(3)
    
    

    rate.sleep()
