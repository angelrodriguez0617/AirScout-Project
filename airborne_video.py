import movement as mov
import cv2 as cv
from time import sleep
import cv2 as cv
import shutil
import threading
import os
from check_camera import w,h

path = "Default"
parent_directory = os.getcwd()
directory = str('dataset_5')
path = os.path.join(parent_directory, directory)
if os.path.isdir(directory):
    shutil.rmtree(directory)
os.mkdir(path)
os.chdir(path)

def extract_pictures(video, mv):
    '''Extract pictures from drone's camera'''
    try:
        drone = mv.get_drone()
        count = 0
        img_num = 1
        frame_read = drone.get_frame_read()
        # video = cv.VideoWriter(f'{directory}.mp4', cv.VideoWriter_fourcc(*'XVID'), 30, (width, height))
        while True:
            if count%30 == 0:
                cv.imwrite(f'{directory}_img{img_num}.png', frame_read.frame)
                img_num += 1
            count += 1
            video.write(frame_read.frame)
            sleep(1/60)
    
    except KeyboardInterrupt: # Supposed to come here after pressing ctrl + c
        # Video must be released, otherwise, saved video will be corrupted.
        video.release()

if __name__ == "__main__":
    # Initialize drone object and take off
    drone = mov.movement()
    # Austin says this might work
    sleep(0.1)

    camera = drone.get_drone()
    if camera.get_battery() < 20: # if battery is under 20%
        print("\n" + ">>>>>>>>>>>>>>>> DRONE BATTERY LOW. CHANGE BATTERY!")

    x_step = 100 # Steps the drone takes fowards and backwards
    y_step = 100 # Steps the drone takes left and right
    x_boundary = 900 # X-axis boundary of path
    y_boundary = 500 # Y-axis boundary of path

    # Record video and pictures
    try:
        frame_read = camera.get_frame_read()
        # Default size of frame which will be changed
        height, width, _ = frame_read.frame.shape
        height, width = h,w
        video = cv.VideoWriter(f'{directory}video.mp4', cv.VideoWriter_fourcc(*'mp4v'), 30, (width, height))
        video_thread = threading.Thread(target=extract_pictures, args=(video, drone))
        video_thread.start()
        # img_num should equal 10 after this meaning 10 photos were taken
        
        temp_x_coordinate = drone.get_x_location()
        temp_y_coordinate = drone.get_y_location()
        while drone.get_y_location() <= y_boundary: # The snake path progressively moves towards the y_boundary which should be the end of its mission 
            while drone.get_x_location() + x_step <= x_boundary: # Keep moving forward until the x_boundary is reached
                drone.move(fwd=x_step)
            if drone.get_y_location() + y_step <= y_boundary: # We should pass into here every time except when we are on the y_boundary
                # Continue to the next row of the snake path search algorithm
                drone.move(left=y_step)
            else: # When here, we should be done with the mission, so exit the while loop
                break
            while drone.get_x_location() > 0: # Move all the way back to x=0, we are okay with the drone being a step behind x=0
                drone.move(back=x_step)
            if drone.get_y_location() + y_step <= y_boundary: # We should pass into here every time except when we are on the y_boundary
                # Continue to the next row of the snake path search algorithm
                drone.move(left=y_step)
            else: # When here, we should be done with the mission, so exit the while loop
                break

        print("\n >>>>>>>>>>>>>>>> OUTSIDE OF THE WHILE LOOP\n")
        drone.move(cw=180)
        drone.go_to(0,0,0)
        video.release()
        drone.land(turn_off=True)
    except KeyboardInterrupt: # keyboard key combination of “CTRL + C” or “CTRL + Z”
        # End the video so that it is not corrupted
        video.release()
        drone.land(turn_off=True)

      
        
        