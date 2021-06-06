import numpy as np
import pybullet as p
import itertools

class Robot():
    """ 
    The class is the interface to a single robot
    """
    def __init__(self, init_pos, robot_id, dt):
        self.id = robot_id
        self.dt = dt
        self.state = 0
        self.pybullet_id = p.loadSDF("../models/robot.sdf")[0]
        self.joint_ids = list(range(p.getNumJoints(self.pybullet_id)))
        self.initial_position = init_pos
        self.reset()

        # No friction between bbody and surface.
        p.changeDynamics(self.pybullet_id, -1, lateralFriction=5., rollingFriction=0.)

        # Friction between joint links and surface.
        for i in range(p.getNumJoints(self.pybullet_id)):
            p.changeDynamics(self.pybullet_id, i, lateralFriction=5., rollingFriction=0.)
            
        self.messages_received = []
        self.messages_to_send = []
        self.neighbors = []
        

    def reset(self):
        """
        Moves the robot back to its initial position 
        """
        p.resetBasePositionAndOrientation(self.pybullet_id, self.initial_position, (0., 0., 0., 1.))
            
    def set_wheel_velocity(self, vel):
        """ 
        Sets the wheel velocity,expects an array containing two numbers (left and right wheel vel) 
        """
        assert len(vel) == 2, "Expect velocity to be array of size two"
        p.setJointMotorControlArray(self.pybullet_id, self.joint_ids, p.VELOCITY_CONTROL,
            targetVelocities=vel)

    def get_pos_and_orientation(self):
        """
        Returns the position and orientation (as Yaw angle) of the robot.
        """
        pos, rot = p.getBasePositionAndOrientation(self.pybullet_id)
        euler = p.getEulerFromQuaternion(rot)
        return np.array(pos), euler[2]
    
    def get_messages(self):
        """
        returns a list of received messages, each element of the list is a tuple (a,b)
        where a= id of the sending robot and b= message (can be any object, list, etc chosen by user)
        Note that the message will only be received if the robot is a neighbor (i.e. is close enough)
        """
        return self.messages_received
        
    def send_message(self, robot_id, message):
        """
        sends a message to robot with id number robot_id, the message can be any object, list, etc
        """
        self.messages_to_send.append([robot_id, message])
        
    def get_neighbors(self):
        """
        returns a list of neighbors (i.e. robots within 2m distance) to which messages can be sent
        """
        return self.neighbors     
    def desired_distance_line(self,robot_id,  m):
        """
        set a list of desired distance, using robot_id to pick
        """        
        desired_distance_y = np.array([[0,-0.5*0.9,-1*0.9,-1.5*0.9,-2*0.9,-2.5*0.9],
                                       [0.5*0.9,0,-0.5*0.9,-1*0.9,-1.5*0.9,-2*0.9],
                                       [1*0.9,0.5*0.9,0,-0.5*0.9,-1*0.9,-1.5*0.9],
                                       [1.5*0.9,1*0.9,0.5*0.9,0,-0.5*0.9,-1*0.9],
                                       [2*0.9,1.5*0.9,1*0.9,0.5*0.9,0,-0.5*0.9],
                                       [2.5*0.9,2*0.9,1.5*0.9,1*0.9,0.5*0.9,0]])
        
        desired_distance_x = 0
        desired_distance_neighbour_x = 0
        desired_distance_neighbour_y= desired_distance_y[robot_id][m[0]]
        
        return desired_distance_neighbour_x, desired_distance_neighbour_y
    
    def desired_distance_circle2(self,robot_id, m):
        desired_circle2_x = np.array([[0,0.866,0.866,0,-0.866,-0.866],
                                       [-0.866,0,0,-0.866,-0.866*2,-0.866*2],
                                       [-0.866,0,0,-0.866,-0.866*2,-0.866*2],
                                       [0,0.866,0.866,0,-0.866,-0.866],
                                       [0.866,0.866*2,0.866*2,0.866,0,0],
                                       [0.866,0.866*2,0.866*2,0.866,0,0]])
        
        desired_circle2_y = np.array([[0,0.5,1.5,2,1.5,0.5],
                                       [-0.5,0,1,1.5,1,0],
                                       [-1.5,-1,0,0.5,0,-1],
                                       [-2,-1.5,-0.5,0,-0.5,-1.5],
                                       [-1.5,-1,0,0.5,0,-1],
                                       [-0.5,0,1,1.5,1,0]])
        desired_circle2_neighbour_x = desired_circle2_x[m[0]][robot_id]
        desired_circle2_neighbour_y= desired_circle2_y[m[0]][robot_id]
        
        return desired_circle2_neighbour_x, desired_circle2_neighbour_y
  
    
    
    def desired_distance_circle1(self,robot_id,  m):
        desired_circle1_x = np.array([[0,0.866*0.4,0.866*0.4,0,-0.866*0.4,-0.866*0.4],
                                       [-0.866*0.4,0,0,-0.866*0.4,-0.866*2*0.4,-0.866*2*0.4],
                                       [-0.866*0.4,0,0,-0.866*0.4,-0.866*2*0.4,-0.866*2*0.4],
                                       [0,0.866*0.4,0.866*0.4,0,-0.866*0.4,-0.866*0.4],
                                       [0.866*0.4,0.866*2*0.4,0.866*2*0.4,0.866*0.4,0,0],
                                       [0.866*0.4,0.866*2*0.4,0.866*2*0.4,0.866*0.4,0,0]])
        
        desired_circle1_y = np.array([[0,0.5*0.4,1.5*0.4,2*0.4,1.5*0.4,0.5*0.4],
                                       [-0.5*0.4,0,1*0.4,1.5*0.4,1*0.4,0],
                                       [-1.5*0.4,-1*0.4,0,0.5*0.4,0,-1*0.4],
                                       [-2*0.4,-1.5*0.4,-0.5*0.4,0,-0.5*0.4,-1.5*0.4],
                                       [-1.5*0.4,-1*0.4,0,0.5*0.4,0,-1*0.4],
                                       [-0.5*0.4,0,1*0.4,1.5*0.4,1*0.4,0]])
        desired_circle1_neighbour_x = desired_circle1_x[m[0]][robot_id]
        desired_circle1_neighbour_y= desired_circle1_y[m[0]][robot_id]
        
        return desired_circle1_neighbour_x, desired_circle1_neighbour_y
    def desired_distance_line2(self,robot_id,  m):
        desired_distance2_y = np.array([[0,-0.5*0.9,-1*0.9,-1.5*0.9,-2*0.9,-2.5*0.9],
                                       [0.5*0.9,0,-0.5*0.9,-1*0.9,-1.5*0.9,-2*0.9],
                                       [1*0.9,0.5*0.9,0,-0.5*0.9,-1*0.9,-1.5*0.9],
                                       [1.5*0.9,1*0.9,0.5*0.9,0,-0.5*0.9,-1*0.9],
                                       [2*0.9,1.5*0.9,1*0.9,0.5*0.9,0,-0.5*0.9],
                                       [2.5*0.9,2*0.9,1.5*0.9,1*0.9,0.5*0.9,0]])
        
        desired_distance2_x = 0
        desired_distance2_neighbour_x = 0
        desired_distance2_neighbour_y= desired_distance2_y[m[0]][robot_id]
        
        return desired_distance2_neighbour_x, desired_distance2_neighbour_y
    def diamond(self,robot_id,  m):
        diamond_x=np.array([[0,0.5*0.9,0,-0.5*0.9,-0.5*0.9,-0.5*0.9],
                            [-0.5*0.9,0,-0.5*0.9,-1*0.9,-1*0.9,-1*0.9],
                            [0,0.5*0.9,0,-0.5*0.9,-0.5*0.9,-0.5*0.9],
                            [0.5*0.9,1*0.9,0.5*0.9,0,0,0],
                            [0.5*0.9,1*0.9,0.5*0.9,0,0,0],
                            [0.5*0.9,1*0.9,0.5*0.9,0,0,0]])
        diamond_y=np.array([[0,1*0.9,2*0.9,1.5*0.9,1*0.9,0.5*0.9],
                            [-1*0.9,0,1*0.9,0.5*0.9,0,-0.5*0.9],
                            [-2*0.9,-1*0.9,0,-0.5*0.9,-1*0.9,-1.5*0.9],
                            [-1.5*0.9,-0.5*0.9,0.5*0.9,0,-0.5*0.9,-1*0.9],
                            [-1*0.9,0,1*0.9,0.5*0.9,0,-0.5*0.9],
                            [-0.5*0.9,0.5*0.9,1.5*0.9,1*0.9,0.5*0.9,0]])
        diamond_x = diamond_x[m[0]][robot_id]
        diamond_y= diamond_y[m[0]][robot_id]
        
        return diamond_x, diamond_y
    def compute_controller(self):
        """ 
        function that will be called each control cycle which implements the control law
        TO BE MODIFIED
        
        we expect this function to read sensors (built-in functions from the class)
        and at the end to call set_wheel_velocity to set the appropriate velocity of the robots
        """
        
        # here we implement an example for a consensus algorithm
        neig = self.get_neighbors()
        messages = self.get_messages()
        pos, rot = self.get_pos_and_orientation()
        
          #send message of positions to all neighbors indicating our position
        for n in neig:
            self.send_message(n, [pos, self.state])
         
        #set up formation control law to compose a square 
        

       
        # check if we received the position of our neighbors and compute desired change in position
        # as a function of the neighbors (message is composed of [neighbors id, position])
        #add desired distance for square
        
        dx = 0.
        dy = 0.
        
   #line moving follow a leader--5    
        if self.state == 0:
            if self.id == 5 :
                  if messages:
                    for m in messages:
                        
                        desired_distance_neighbour_x, desired_distance_neighbour_y = self.desired_distance_line(self.id, m)


                        dx += - pos[0] + 2.5 
                        dy += - pos[1] + 10

            #             # integrate?what is this used for?
            #             des_pos_x = pos[0] + self.dt * dx
            #             des_pos_y = pos[1] + self.dt * dy


                    #computem and make a circle formation outside velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 0.1*np.sin(des_theta-rot)*vel_norm + 0.1*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -0.1*np.sin(des_theta-rot)*vel_norm + 0.1*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])

                    erro_leader = 10 - pos[1]
                   
                    if erro_leader < 2:
                        self.state = 1
                    
            else:
                if messages:
                    for m in messages:
                        desired_distance_neighbour_x, desired_distance_neighbour_y = self.desired_distance_line(self.id, m)
                        if m[0] == 5 and m[1][1] == 1:
                            self.state = 1
                            
                        dx += m[1][0][0] - pos[0] + desired_distance_neighbour_x 
                        dy += m[1][0][1] - pos[1] + desired_distance_neighbour_y 

#                     # integrate?what is this used for?
#                     des_pos_x = pos[0] + self.dt * dx
#                    veral tasks to achieve: des_pos_y = pos[1] + self.dt * dy


                    #compute velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 11*np.sin(des_theta-rot)*vel_norm + 11*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -11*np.sin(des_theta-rot)*vel_norm + 11*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])
     #circle2 formation              
                  
        elif self.state == 1:
            
            if messages:
                    for m in messages:
                        if self.id == 5 and (pos[1]-6.5) < 0.1:
                            self.state = 2
                                                       
                        elif m[0] == 5 and m[1][1] == 2:
                            self.state = 2
#                         elif self.id == 0:
#                             print(pos[0],pos[1])
                            
                        desired_circle2_neighbour_x, desired_circle2_neighbour_y = self.desired_distance_circle2(self.id, m)

                        dx += m[1][0][0] - pos[0] + desired_circle2_neighbour_x 
                        dy += m[1][0][1] - pos[1] + desired_circle2_neighbour_y 

                    # integrate?what is this used for?
                    des_pos_x = pos[0] + self.dt * dx
                    des_pos_y = pos[1] + self.dt * dy


                    #compute velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 5*np.sin(des_theta-rot)*vel_norm + 5*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -5*np.sin(des_theta-rot)*vel_norm + 5*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])
                    
   #circle2 moving follow leader 0            
        elif self.state == 2:
            
            if self.id == 0 :
                  if messages:
                    for m in messages:
                        
#                         desired_distance_neighbour_x, desired_distance_neighbour_y = self.desired_distance_line(self.id, m)


                        dx += - pos[0] + 2.5 
                        dy += - pos[1] + 3

            #             # integrate?what is this used for?
            #             des_pos_x = pos[0] + self.dt * dx
            #             des_pos_y = pos[1] + self.dt * dy


                    #computem and make a circle formation outside velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 0.8*np.sin(des_theta-rot)*vel_norm + 0.8*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -0.8*np.sin(des_theta-rot)*vel_norm + 0.8*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])

                    erro_leader = pos[1]-3
                    
                    
                    if erro_leader < 0.1:
                        self.state = 3
                    
            else:
                if messages:
                    for m in messages:
                        desired_circle2_neighbour_x, desired_circle2_neighbour_y = self.desired_distance_circle2(self.id, m)
                        if m[0] == 0 and m[1][1] == 3:
                            self.state = 3
                            
                        dx += m[1][0][0] - pos[0] + desired_circle2_neighbour_x 
                        dy += m[1][0][1] - pos[1] + desired_circle2_neighbour_y 

#                     # integrate?what is this used for?
#                     des_pos_x = pos[0] + self.dt * dx
#                    veral tasks to achieve: des_pos_y = pos[1] + self.dt * dy


                    #compute velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 8*np.sin(des_theta-rot)*vel_norm + 8*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -8*np.sin(des_theta-rot)*vel_norm + 8*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])

                    
#move ball to purple follow leader 0
        elif self.state == 3:
            
            if self.id == 0 :
                  if messages:
                    for m in messages:
                        
#                         desired_distance_neighbour_x, desired_distance_neighbour_y = self.desired_distance_line(self.id, m)


                        dx += - pos[0] + 2.4 
                        dy += - pos[1] + 6

            #             # integrate?what is this used for?
            #             des_pos_x = pos[0] + self.dt * dx
            #             des_pos_y = pos[1] + self.dt * dy


                    #computem and make a circle formation outside velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 0.1*np.sin(des_theta-rot)*vel_norm + 0.1*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -0.1*np.sin(des_theta-rot)*vel_norm + 0.1*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])

                    erro_leader = 6-pos[1]
                    
                    
                    if erro_leader < 1:
                        self.state = 4
                  
            else:
                if messages:
                    for m in messages:
                        desired_circle1_neighbour_x, desired_circle1_neighbour_y = self.desired_distance_circle1(self.id, m)
                        if m[0] == 0 and m[1][1] == 4:
                            self.state = 4
                            
                        dx += m[1][0][0] - pos[0] + desired_circle1_neighbour_x 
                        dy += m[1][0][1] - pos[1] + desired_circle1_neighbour_y 

#                     # integrate?what is this used for?
#                     des_pos_x = pos[0] + self.dt * dx
#                    veral tasks to achieve: des_pos_y = pos[1] + self.dt * dy


                    #compute velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 8*np.sin(des_theta-rot)*vel_norm +8*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -8*np.sin(des_theta-rot)*vel_norm + 8*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])
                    
       #circle2 formation              
                  
#         elif self.state == 4:
            
#             if messages:
#                     for m in messages:
                                         
#                         desired_circle2_neighbour_x, desired_circle2_neighbour_y = self.desired_distance_circle2(self.id, m)

#                         dx += m[1][0][0] - pos[0] + desired_circle2_neighbour_x 
#                         dy += m[1][0][1] - pos[1] + desired_circle2_neighbour_y 

#                     # integrate?what is this used for?
#                     des_pos_x = pos[0] + self.dt * dx
#                     des_pos_y = pos[1] + self.dt * dy


#                     #compute velocity change for the wheels
#                     vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
#                     if vel_norm < 0.01:
#                         vel_norm = 0.01
#                     des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
#                     right_wheel = 5*np.sin(des_theta-rot)*vel_norm + 5*np.cos(des_theta-rot)*vel_norm
#                     left_wheel = -5*np.sin(des_theta-rot)*vel_norm + 5*np.cos(des_theta-rot)*vel_norm
#                     self.set_wheel_velocity([left_wheel, right_wheel])
                    
                    
#circle2 moving follow leader 0           
        elif self.state == 4:
            
            if self.id == 1 :
                  if messages:
                    for m in messages:

                        dx += - pos[0] + 6.1
                        dy += - pos[1] + 4.9

            #             # integrate?what is this used for?
            #             des_pos_x = pos[0] + self.dt * dx
            #             des_pos_y = pos[1] + self.dt * dy


                    #computem and make a circle formation outside velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 0.1*np.sin(des_theta-rot)*vel_norm + 0.1*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -0.1*np.sin(des_theta-rot)*vel_norm + 0.1*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])

                    erro_leader = 6.1-pos[0]
   
                    if erro_leader < 1:
                        self.state = 5
                    
            else:
                if messages:
                    for m in messages:
                        desired_circle2_neighbour_x, desired_circle2_neighbour_y = self.desired_distance_circle2(self.id, m)
                        if m[0] == 1 and m[1][1] == 5:
                            self.state = 5
                            
                        dx += m[1][0][0] - pos[0] + desired_circle2_neighbour_x 
                        dy += m[1][0][1] - pos[1] + desired_circle2_neighbour_y 

#                     # integrate?what is this used for?
#                     des_pos_x = pos[0] + self.dt * dx
#                    veral tasks to achieve: des_pos_y = pos[1] + self.dt * dy


                    #compute velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 5*np.sin(des_theta-rot)*vel_norm + 5*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -5*np.sin(des_theta-rot)*vel_norm + 5*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])
                    
                    
                    
                    
    #circle2 moving follow leader 0           
        elif self.state == 5:
            
            if self.id == 0 :
                  if messages:
                    for m in messages:
                        
#                         desired_distance_neighbour_x, desired_distance_neighbour_y = self.desired_distance_line(self.id, m)


                        dx += - pos[0] + 4.5 
                        dy += - pos[1] + 0 

            #             # integrate?what is this used for?
            #             des_pos_x = pos[0] + self.dt * dx
            #             des_pos_y = pos[1] + self.dt * dy


                    #computem and make a circle formation outside velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 0.5*np.sin(des_theta-rot)*vel_norm + 0.5*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -0.5*np.sin(des_theta-rot)*vel_norm + 0.5*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])

                    erro_leader = pos[1]
   
                    if erro_leader < 0.5:
                        self.state = 6
            
            
                    
            else:
                if messages:
                    for m in messages:
                        desired_circle2_neighbour_x, desired_circle2_neighbour_y = self.desired_distance_circle2(self.id, m)
                        if m[0] == 0 and m[1][1] == 6:
                            self.state = 6
                            
                        dx += m[1][0][0] - pos[0] + desired_circle2_neighbour_x 
                        dy += m[1][0][1] - pos[1] + desired_circle2_neighbour_y 

#                     # integrate?what is this used for?
#                     des_pos_x = pos[0] + self.dt * dx
#                    veral tasks to achieve: des_pos_y = pos[1] + self.dt * dy


                    #compute velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 11*np.sin(des_theta-rot)*vel_norm + 11*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -11*np.sin(des_theta-rot)*vel_norm + 11*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])
                    
                   
                    
#move ball to red follow leader3
        elif self.state == 6:
            
            if self.id == 3 :
                  if messages:
                    for m in messages:
                        
#                         desired_distance_neighbour_x, desired_distance_neighbour_y = self.desired_distance_line(self.id, m)


                        dx += - pos[0] + 0.2
                        dy += - pos[1] + 6

            #             # integrate?what is this used for?
            #             des_pos_x = pos[0] + self.dt * dx
            #             des_pos_y = pos[1] + self.dt * dy


                    #computem and make a circle formation outside velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 0.2*np.sin(des_theta-rot)*vel_norm + 0.2*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -0.2*np.sin(des_theta-rot)*vel_norm + 0.2*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel])

                    erro_leader = (6-pos[1])*(6-pos[1])
                    
                    
                    if erro_leader < 1:
                        self.state = 7
                    print(self.id,self.state,pos[0],pos[1])
            else:
                if messages:
                    for m in messages:
                        desired_circle1_neighbour_x, desired_circle1_neighbour_y = self.desired_distance_circle1(self.id, m)
                        if m[0] == 3 and m[1][1] == 7:
                            self.state = 7
                            
                        dx += m[1][0][0] - pos[0] + desired_circle1_neighbour_x 
                        dy += m[1][0][1] - pos[1] + desired_circle1_neighbour_y 

#                     # integrate?what is this used for?
#                     des_pos_x = pos[0] + self.dt * dx
#                    veral tasks to achieve: des_pos_y = pos[1] + self.dt * dy


                    #compute velocity change for the wheels
                    vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
                    if vel_norm < 0.01:
                        vel_norm = 0.01
                    des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
                    right_wheel = 8*np.sin(des_theta-rot)*vel_norm +8*np.cos(des_theta-rot)*vel_norm
                    left_wheel = -8*np.sin(des_theta-rot)*vel_norm + 8*np.cos(des_theta-rot)*vel_norm
                    self.set_wheel_velocity([left_wheel, right_wheel]) 
                    
                    

# #       deform as a line     
#             if self.id == 1:
#                   if messages:
#                     for m in messages:
                        
#                         desired_distance2_neighbour_x, desired_distance2_neighbour_y = self.desired_distance_line2(self.id, m)


#                         dx += - pos[0] + 2.5 
#                         dy += - pos[1] + 10

#             #             # integrate?what is this used for?
#             #             des_pos_x = pos[0] + self.dt * dx
#             #             des_pos_y = pos[1] + self.dt * dy


#                     #computem and make a circle formation outside velocity change for the wheels
#                     vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
#                     if vel_norm < 0.01:
#                         vel_norm = 0.01
#                     des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
#                     right_wheel = 0.1*np.sin(des_theta-rot)*vel_norm + 0.1*np.cos(des_theta-rot)*vel_norm
#                     left_wheel = -0.1*np.sin(des_theta-rot)*vel_norm + 0.1*np.cos(des_theta-rot)*vel_norm
#                     self.set_wheel_velocity([left_wheel, right_wheel])

#                     erro_leader = 10- pos[1]
                   
# #                     if erro_leader < 0.3:
# #                         self.state = 9
                    
#             else:
#                 if messages:
#                     for m in messages:
# #                        desired_distance2_neighbour_x, desired_distance2_neighbour_y = self.desired_distance_line2(self.id, m)
# #                         if m[0] == 4 and m[1][1] == 9:
# #                             self.state = 9
                            
#                         dx += m[1][0][0] - pos[0]
#                         dy += m[1][0][1] - pos[1]

# #                     # integrate?what is this used for?
# #                     des_pos_x = pos[0] + self.dt * dx
# #                    veral tasks to achieve: des_pos_y = pos[1] + self.dt * dy


#                     #compute velocity change for the wheels
#                     vel_norm = np.linalg.norm([dx, dy]) #norm of desired velocity
#                     if vel_norm < 0.01:
#                         vel_norm = 0.01
#                     des_theta = np.arctan2(dy/vel_norm, dx/vel_norm)
#                     right_wheel = 2*np.sin(des_theta-rot)*vel_norm + 2*np.cos(des_theta-rot)*vel_norm
#                     left_wheel = -2*np.sin(des_theta-rot)*vel_norm + 2*np.cos(des_theta-rot)*vel_norm
#                     self.set_wheel_velocity([left_wheel, right_wheel])         
                    
                    