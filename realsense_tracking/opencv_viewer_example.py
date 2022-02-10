## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import json
import time, math, os.path
import pyrealsense2 as rs
import numpy as np
import cv2
print("opencv version : " + cv2.__version__ )

file_calib_json = 'calib_pos.json'

import serial
from serial.tools import list_ports
com_ports = list_ports.comports()
print("com ports")
for com_port in com_ports:
    print("  " + com_port.description + " " + com_port.device)
our_port = 'COM8'
ser = serial.Serial(our_port, 115200, timeout=1)
time.sleep(1)
print("serial connected : {}".format(ser.readline().decode()))

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

# config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 6)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
# config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 6)

# Start streaming
pipeline.start(config)
print("pipeline started")


# https://docs.opencv.org/4.5.5/d4/d26/samples_2cpp_2facedetect_8cpp-example.html
# https://opencv-tutorial.readthedocs.io/en/latest/face/face.html
# https://www.geeksforgeeks.org/face-detection-using-cascade-classifier-using-opencv-python/
# https://towardsdatascience.com/real-time-head-pose-estimation-in-python-e52db1bc606a

def serial_write_and_read(ser_com):
    ser.reset_input_buffer()
    ser.write("{}\n".format(ser_com).encode())
    ser.flush()
    return ser.readline().decode()

def serial_move(point):
    print("{}".format(serial_write_and_read("a {}".format(point[0]))))
    print("{}".format(serial_write_and_read("b {}".format(point[1]))))
    time.sleep(0.2)

def my_mouse(event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN :
            print("click")
            ser.reset_input_buffer()
            ser.write(("raw\n".encode()))
            mir_pos = ser.readline().decode().split(',')
            mir_pos_x = int( mir_pos[0])
            mir_pos_y = int( mir_pos[1])
            if (face_point[2] > 0):
                data_str = "{:.0f},{:.0f},{:.3f}, {}, {}".format(face_point[0], face_point[1], face_point[2], mir_pos_x, mir_pos_y)
                print( data_str )
                if (calibration_loop) :
                    calib_results.append([face_point, [mir_pos_x, mir_pos_y]])

def find_closest(point) :
    min_dist_sqr = 1000000000
    closest_point = []
    distances = []
    for calib_point in calib_results:
        cur_dist_sqr = 0
        cur_dist_sqr += (calib_point[0][0] - point[0]) **2
        cur_dist_sqr += (calib_point[0][1] - point[1]) **2
        cur_dist_sqr += (100*calib_point[0][2] - 100*point[2]) **2
        if (min_dist_sqr > cur_dist_sqr) :
            min_dist_sqr = cur_dist_sqr
            closest_point = calib_point[1]
        dist_point = [math.sqrt(cur_dist_sqr), calib_point[1]]
        distances.append(dist_point)
    sorted(distances, key=lambda l:l[0])
    print ("min dist found {} for {}".format(math.sqrt(min_dist_sqr), closest_point))
    return closest_point

# init globalsss
face_point = [-1, -1, -1]
calibration_loop = False
enable_follow = False
calib_points = []
calib_active_index = 0
calib_step_start_time_s = 0
if os.path.exists(file_calib_json) :
    with open(file_calib_json, 'r') as calib_file:
        calib_results = json.load(calib_file)
else :
    calib_results = []


# ========================
# open window and callbacks
cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback('RealSense',my_mouse)

try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))

        gray_image = cv2.cvtColor( color_image, cv2.COLOR_BGR2GRAY )
        haar_cascade = cv2.CascadeClassifier('xml/haarcascade_frontalface_default.xml')
        faces_rect = haar_cascade.detectMultiScale( gray_image, scaleFactor=1.1, minNeighbors=9)
        

        if (len(faces_rect) == 1):
            for (x, y, w, h) in faces_rect:
                
                cv2.rectangle(images, (x, y), (x+w, y+h), (0, 255, 0), thickness=2)
                xm = math.floor(x + w/2)
                ym = math.floor(y + h/2)
                dist = depth_frame.get_distance(xm, ym)
                cv2.putText(images, "{:.0f} {:.0f} {:.3f}".format(xm,ym,dist), (xm,ym), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )
                face_point = [xm, ym, dist]
        else :
            face_point = [-1,-1, -1]
  

        # Show images

        cv2.imshow('RealSense', images)

        key = cv2.waitKey(1)
        if(key == ord('q') or key == ord('Q')):
            print("quiting")
            break
        elif (key == ord('o')):
            print("{}".format(serial_write_and_read("o")))
        elif (key == ord('i')):
            print("{}".format(serial_write_and_read("i")))
        elif (key == ord('p')):
            print("{}".format(serial_write_and_read("p")))
        elif (key == ord('l')):
            print("{}".format(serial_write_and_read("l")))
        elif (key == ord('O')):
            print("{}".format(serial_write_and_read("O")))
        elif (key == ord('I')):
            print("{}".format(serial_write_and_read("I")))
        elif (key == ord('P')):
            print("{}".format(serial_write_and_read("P")))
        elif (key == ord('L')):
            print("{}".format(serial_write_and_read("L")))
        elif (key == ord('1')):
            print("{}".format(serial_write_and_read("1")))
        elif (key == ord('2')):
            print("{}".format(serial_write_and_read("2")))      
        elif (key == ord('3')):
            print("{}".format(serial_write_and_read("3")))
        elif (key == ord('4')):
            print("{}".format(serial_write_and_read("4")))
        elif (key == ord('5')):
            print("{}".format(serial_write_and_read("5")))  
        elif (key == ord('6')):
            print("{}".format(serial_write_and_read("6")))

        elif (key == ord('c')):
            calibration_loop = True
            enable_follow = False
            calib_results = []
            calib_active_index = 0
            step = 20
            start = 50
            end = 130
            start_modx = start % (step*2)
            for x in range(start, end+1, step):
                if x % (step*2) == start_modx :
                    y_range = range(start, end+1, step)
                else :
                    y_range = reversed(range(start, end+1, step))
                for y in y_range:
                    calib_points.append([x,y])
            serial_move(calib_points[0])
            calib_step_start_time_s = time.perf_counter()

        elif (key == ord('a') or key == ord('A')):
            ser.reset_input_buffer()
            ser.write(("raw\n".encode()))
            mir_pos = ser.readline().decode()
            if (face_point[2] > 0):
                data_str = "{:.0f},{:.0f},{:.3f}, {}".format(face_point[0], face_point[1], face_point[2], mir_pos)
                print( data_str )

        elif (key == ord('f')) :
            if not calibration_loop:
                enable_follow = not enable_follow
            print("enable folow {}".format(enable_follow))

        if calibration_loop :
            # move the mirror until done, then close the calib loop
            if (time.perf_counter() - calib_step_start_time_s > 10 ) :
                calib_active_index += 1
                if (calib_active_index < len(calib_points)):
                    point = calib_points[calib_active_index]
                    serial_move(calib_points[calib_active_index])
                    calib_step_start_time_s = time.perf_counter()
                else :
                    calibration_loop = False
                    with open(file_calib_json, 'w') as calib_file:
                        json.dump(calib_results, calib_file, ensure_ascii=False, indent=4)

        if enable_follow:
            if (face_point[2] > 0) :
                set_point = find_closest(face_point)
                if (len(set_point) > 0 ):
                    serial_move(set_point)


finally:
    print("Stop streaming")
    cv2.destroyAllWindows()
    ser.close()
    # time.sleep(1)
    # exit(0)
    pipeline.stop()
    quit()

