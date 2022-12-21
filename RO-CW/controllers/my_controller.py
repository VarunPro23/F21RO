from controller import Robot
from datetime import datetime
from timeit import default_timer as timer
import math
import sys
import numpy as np

class Controller:
    def __init__(self, robot):        
        # Robot Parameters
        self.robot = robot
        self.time_step = 32 # ms
        self.max_speed = 6.28  # ms # Refers to the max speed of the robot
        self.min_speed = -6.28 # ms # This is in negative to ensure the robot can turn

        #Excerpt of code taken from lab 1
 
        # Enable Motors
        # Initialize motors
        self.left_motor = self.robot.getDevice('left wheel motor')
        self.right_motor = self.robot.getDevice('right wheel motor') 

        # Initialize the position of the motors
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))

        # Initialize the velocity of the motors. It is set to 0
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

        # Initialize the speed of the wheels. It is set to 0 to ensure it doesnt move.
        self.left_speed = 0
        self.right_speed = 0
    
        # Enable Proximity Sensors
        self.prox_sensor = []   # An array to store the proximity sensor values
        for i in range(8):      # For loop to initialize the array. There are 8 sensors on the robot
            sensor_name = 'ps' + str(i)
            self.prox_sensor.append(self.robot.getDevice(sensor_name)) 
            self.prox_sensor[i].enable(self.time_step)
       
        # Enable Ground Sensors
        # The ground sensors are used to detect the ground and any changes to the arena
        self.left_ir = self.robot.getDevice('gs0')
        self.left_ir.enable(self.time_step)
        self.center_ir = self.robot.getDevice('gs1')
        self.center_ir.enable(self.time_step)
        self.right_ir = self.robot.getDevice('gs2')
        self.right_ir.enable(self.time_step)
        
    # Own Code

        # A Boolean variable is initialized to check whether there is a balck box on the ground or not
        self.obj=False # At the start, no black is detected and thus, set to false
        
        # A variable to store the time when the robot starts to move
        self.start_time=timer()
        
    # The function is used to check if there is a black patch in the arena    
    def obj_arena(self):
          if self.center_ir.getValue() < 350: # If ground sensor detects a value less than 350, a black patch is detected
              self.obj=True # The boolean variable is changed to True
              print('Black patch has been detected')
                           
    def run_robot(self):        
        # Main Loop
        while self.robot.step(self.time_step) != -1:
            # Read Ground Sensors
            left = self.left_ir.getValue() 
            center = self.center_ir.getValue()
            right = self.right_ir.getValue()
          
            # Read Distance Sensors
            leftwall = self.prox_sensor[5].getValue()   # Proximity sensor number 5 detects the left wall
            rightwall= self.prox_sensor[2].getValue()   # Proximity sensor number 2 detects the right wall
            frontwall= (self.prox_sensor[0].getValue() + self.prox_sensor[7].getValue()) / 2    # Two sensors are used to detect the front wall       
            
            
            # Checks if a black patch has been detected
            if self.obj==True:                   
                frontwall= self.prox_sensor[7].getValue()   # If black patch has been detected, sensor 7 is used to detect walls in front after turning right. This ensures the bot doesnt oversteer
                
            else:
                frontwall= self.prox_sensor[0].getValue()   # If black patch has been detected, sensor 0 is used to detect walls in front after turning left. This ensures the bot doesnt oversteer

            if frontwall:   # If a frontwall is not detected, the robot moves straight.
                print("Rat moves forward")
                self.left_speed = self.max_speed
                self.right_speed = self.max_speed
            
            if frontwall > 100:     # If a frontwall is detected, the robot needs to turn according to the environment
                if self.obj==True:  # If black patch was detected, the robot needs to turn right
                    print("Rat moves right")
                    self.left_speed = self.max_speed
                    self.right_speed = self.min_speed

                else:               #If black patch is not detected, the robot needs to turn left
                    print("Rat moves left")
                    self.left_speed = self.min_speed
                    self.right_speed = self.max_speed
                    if(leftwall > 80) or (rightwall > 80):      # This loop makes sure the robot follows a aligned path
                        self.left_speed = self.min_speed/20
                        self.right_speed = self.max_speed

            self.obj_arena()
            
            # This loop is to stop the robot once it reaches the reward zone.
            # When the robot reaches the end of the maze it should stop.
            # When the front four proximity sensors detect walls, the robot should stop 
                      
            if (self.prox_sensor[0].getValue() > 100) and (self.prox_sensor[1].getValue() > 100) and (self.prox_sensor[6].getValue() > 100) and (self.prox_sensor[7].getValue() > 100):
                # Stopping the robot's motors
                self.left_motor.setVelocity(0)                   # Sets the velocity of the left motor
                self.right_motor.setVelocity(0)                  # Right wheel speed is set to 0

                print("Reward zone reached")
                self.curr_time = timer()                            # Variable to store the present time
                time_taken = self.curr_time - self.start_time       # Variable to store the time taken by the robot to complete task.                 
                
                print(f' Time taken = {time_taken}')                # Prints the time taken to complete the task
                sys.exit("System Exiting")
                              
            self.left_motor.setVelocity(self.left_speed)        # Sets the velocity of the left motor
            self.right_motor.setVelocity(self.right_speed)      # Sets the velocity of the right motor

           
if __name__ == "__main__":
    my_robot = Robot()
    controller = Controller(my_robot)
    controller.run_robot()