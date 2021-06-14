import cv2
import numpy as np
import time

try:
    import sim
except:
    print('"sim.py" could not be imported. Check whether "sim.py" or the remoteApi library could not be found. Make sure both are in the same folder as this file')

def load_image(image, resolution):
    return cv2.flip(np.array(image, dtype=np.uint8).reshape((resolution[1], resolution[0], 3)), 0)

def main():
    print('Program Started')
    sim.simxFinish(-1) # just in case, close all opened connections 
    clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5) # establishes a connection between python and coppelia
    if clientID != -1:
        print('Connected to remote API server')
    else:
        print('Failed connecting to remote API server')

    return_code, camera = sim.simxGetObjectHandle(clientID, "kinect_rgb", sim.simx_opmode_oneshot_wait)
    return_code, left_motor = sim.simxGetObjectHandle(clientID, "Pioneer_p3dx_leftMotor", sim.simx_opmode_oneshot_wait)
    return_code, right_motor = sim.simxGetObjectHandle(clientID, "Pioneer_p3dx_rightMotor", sim.simx_opmode_oneshot_wait)
    return_code, pioneer = sim.simxGetObjectHandle(clientID, "Pioneer_p3dx", sim.simx_opmode_oneshot_wait)
    
    sim.simxSetJointTargetVelocity(clientID, left_motor, 0, sim.simx_opmode_streaming)
    sim.simxSetJointTargetVelocity(clientID, right_motor, 0, sim.simx_opmode_streaming)

    return_code, _, _ = sim.simxGetVisionSensorImage(clientID, camera, 0, sim.simx_opmode_streaming)
    return_code, position = sim.simxGetObjectPosition(clientID, pioneer, -1,  sim.simx_opmode_streaming)
    time.sleep(0.5)
    while clientID != -1:
        return_code, resolution, image = sim.simxGetVisionSensorImage(clientID, camera, 0, sim.simx_opmode_buffer)
        if return_code == sim.simx_return_ok:
            # Load image
            frame = load_image(image, resolution)
        
            ########## TODO
            image_height, image_width, _ = frame.shape
            cv2.line(frame, (image_width//2, image_height), (image_width//2, 0), (0,0,255), 3)

            ret, thresh = cv2.threshold(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 10, 255, cv2.THRESH_BINARY_INV)
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if len(contours) != 0:
                cnt = contours[0]
                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    error = int(cx - image_width//2)
                    cv2.putText(frame, str(error), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    if error > 50:
                        left_motor = 1
                    elif abs(error) < 50:
                        speed = 2
                    else:

            ############
            sim.simxSetJointTargetVelocity(clientID, left_motor, 0.2, sim.simx_opmode_streaming)
            sim.simxSetJointTargetVelocity(clientID, right_motor, 0.2, sim.simx_opmode_streaming);	
            cv2.imshow('Robot camera', frame)	
            if cv2.waitKey(1) & 0xFF == 27:
                cv2.destroyAllWindows()
                break

    # Now close the connection to CoppeliaSim:
    sim.simxFinish(clientID)
    # Stop simulation
    sim.simxStopSimulation(clientID,sim.simx_opmode_oneshot_wait)
if __name__ == '__main__':
    main()