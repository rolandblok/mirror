## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

from my_utils import *
from fone_cam import *
from my_aruco import *
from my_pointcloud import *
from my_serial import *

import json
import time, math, os.path
import pyrealsense2 as rs
import numpy as np
import cv2
print("opencv version : " + cv2.__version__ )

WERKPLAATS = True
if WERKPLAATS:
    COM_PORT = "COM8"
    CAMERA_IP = "http://192.168.94.22:4747/video"
else: 
    COM_PORT = "COM4"
    CAMERA_IP = "http://192.168.1.80:4747/video"

ENABLE_FONE = False
ENABLE_RS_FEED = True
ENABLE_RS_POINTCLOUD = True
ENABLE_FACE_DETECTION = True
ENABLE_SERIAL = True

STREAM_WIDTH=640
STREAM_HEIGHT=480

# init globalsss 
file_calib_json = 'calib_pos.json'
face_point = [-1, -1, -1]
calibration_loop = False
calib_mov_av = [MyMovingAverage(1), MyMovingAverage(1)]
enable_follow = False
calib_points = []     # array [[:camera-xyz][:mirror-angles] :for all calib points]
calib_active_index = 0
calib_step_start_time_s = 0
calib_last_adjust_time_ns = time.perf_counter_ns()
if os.path.exists(file_calib_json) :
    with open(file_calib_json, 'r') as calib_file:
        calib_results = json.load(calib_file)
else :
    calib_results = []
mouse_btns = [False, False, False]
mouse_prev = [0, 0]

my_aruco = MyAruco()

# =================
# SERIAL ENABLING

if ENABLE_SERIAL:
    my_serial = MyMirrorSerial(COM_PORT)
else:
    my_serial = MyMirrorSerial("")

# =================
# CAMERA RS ENABLING
# Configure depth and color streams
if ENABLE_RS_FEED:
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
    config.enable_stream(rs.stream.depth, STREAM_WIDTH, STREAM_HEIGHT, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, STREAM_WIDTH, STREAM_HEIGHT, rs.format.bgr8, 30)
    # config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 6)

    # Start streaming
    pipeline.start(config)
    depth_intrinsics = rs.video_stream_profile(pipeline.get_active_profile().get_stream(rs.stream.depth)).get_intrinsics()

    print("pipeline started")


# https://docs.opencv.org/4.5.5/d4/d26/samples_2cpp_2facedetect_8cpp-example.html
# https://opencv-tutorial.readthedocs.io/en/latest/face/face.html
# https://www.geeksforgeeks.org/face-detection-using-cascade-classifier-using-opencv-python/
# https://towardsdatascience.com/real-time-head-pose-estimation-in-python-e52db1bc606a

def my_mouse(event,x,y,flags,param):
    
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_btns[0] = True
        print("click")
        mir_pos = my_serial.read_pos()
        mir_pos_x = int( mir_pos[0])
        mir_pos_y = int( mir_pos[1])
        if (face_point[2] > 0):
            data_str = "{:.0f},{:.0f},{:.3f}, {}, {}".format(face_point[0], face_point[1], face_point[2], mir_pos_x, mir_pos_y)
            print( data_str )
            if (calibration_loop) :
                calib_results.append([face_point, [mir_pos_x, mir_pos_y]])
    if event == cv2.EVENT_LBUTTONUP:
        mouse_btns[0] = False
    if event == cv2.EVENT_RBUTTONDOWN:
        mouse_btns[1] = True
    if event == cv2.EVENT_RBUTTONUP:
        mouse_btns[1] = False
    if event == cv2.EVENT_MBUTTONDOWN:
        mouse_btns[2] = True
    if event == cv2.EVENT_MBUTTONUP:
        mouse_btns[2] = False
    global mouse_prev
    dx, dy = x - mouse_prev[X], y - mouse_prev[Y]
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_prev = (x, y)
        if mouse_btns[0]:
            my_pointcloud.mouse_move_one(dx,dy)
        elif mouse_btns[1]:
            my_pointcloud.mouse_move_two(dx,dy)
        elif mouse_btns[2]:
            my_pointcloud.mouse_move_three(dx,dy)
        
def find_closest_mirror_angle(camera_point) :
    min_dist_sqr = 1000000000
    closest_point_v1 = []
    closest_mirror_v1 = []
    distances = []     # [[distance, [:camera-xyz][:mirror-angles]] :for all calib points]
    for calib_point in calib_results:
        cur_dist_sqr = 0
        cur_dist_sqr += (calib_point[0][0] - camera_point[0]) **2
        cur_dist_sqr += (calib_point[0][1] - camera_point[1]) **2
        cur_dist_sqr += (100*calib_point[0][2] - 100*camera_point[2]) **2
        if (min_dist_sqr > cur_dist_sqr) :
            min_dist_sqr = cur_dist_sqr
            closest_point_v1 = calib_point[0]
            closest_mirror_v1 = calib_point[1]
        dist_point = [math.sqrt(cur_dist_sqr), calib_point[0], calib_point[1]]
        distances.append(dist_point)
    sorted(distances, key=lambda l:l[0])
    print (" D0 {}  ".format( distances[0]))
    print (" D1 {}  ".format( distances[1]))
    print (" D1 {}  ".format( distances[2]))
    d0d1 = distances[0][0] * distances[1][0]
    d1d2 = distances[1][0] * distances[2][0]
    d0d2 = distances[0][0] * distances[2][0]
    ddsum = d0d1 + d1d2 + d0d2
    w0 = d1d2 / ddsum
    w1 = d0d2 / ddsum
    w2 = d0d1 / ddsum
    closest_point_v2 = [0,0,0]
    closest_point_v2[X] = w0 * distances[0][1][X] +  w1 * distances[1][1][X] +  w2 * distances[2][1][X]
    closest_point_v2[Y] = w0 * distances[0][1][Y] +  w1 * distances[1][1][Y] +  w2 * distances[2][1][Y]
    closest_point_v2[Z] = w0 * distances[0][1][Z] +  w1 * distances[1][1][Z] +  w2 * distances[2][1][Z]
    closest_mirror_v2 = [0,0]
    closest_mirror_v2[A] = w0 * distances[0][2][A] +  w1 * distances[1][2][0] +  w2 * distances[2][2][0]
    closest_mirror_v2[B] = w0 * distances[0][2][B] +  w1 * distances[1][2][1] +  w2 * distances[2][2][1]

    print (" Vx camera {} ".format( camera_point ))
    print (" V1 closest camera {} gives angle {} ; min-dist {}".format( closest_point_v1, closest_mirror_v1, math.sqrt(min_dist_sqr)))
    print (" V2 closest camera {} gives angle {} ; ".format(closest_point_v2, closest_mirror_v2))
    return closest_mirror_v1


# ========================
# open window and callbacks
cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
cv2.moveWindow("RealSense", 20, 20)
cv2.namedWindow('Fone', cv2.WINDOW_AUTOSIZE)
cv2.moveWindow("Fone", 20, 660)
cv2.setMouseCallback('RealSense', my_mouse)
cv2.namedWindow('Parameters', cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow('Parameters', 1000, 200)
cv2.createTrackbar('delay_ms', 'Parameters', 500, 1000, empty_fun)

if ENABLE_RS_POINTCLOUD and ENABLE_RS_FEED:
    my_pointcloud = MyPointCloud()
    my_pointcloud.start(pipeline)

if (ENABLE_FONE):
    # open the fone camera feed
    phone_cap = VideoCapture(CAMERA_IP)
    if not phone_cap.isOpened():
        print("no fone camerag ")
        ENABLE_FONE = False


while ENABLE_FONE or ENABLE_RS_FEED:

    # ================
    # Realsense imaging
    if (ENABLE_RS_FEED):
        frameset = pipeline.poll_for_frames()
        if frameset.size() > 0:
            depth_frame = frameset.get_depth_frame()
            color_frame = frameset.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = color_image.shape

            if ENABLE_FACE_DETECTION:
                gray_image = cv2.cvtColor( color_image, cv2.COLOR_BGR2GRAY )
                haar_cascade = cv2.CascadeClassifier('xml/haarcascade_frontalface_default.xml')
                faces_rect = haar_cascade.detectMultiScale( gray_image, scaleFactor=1.1, minNeighbors=9)

                if (len(faces_rect) == 1):
                    for (x, y, w, h) in faces_rect:
                        
                        cv2.rectangle(color_image, (x, y), (x+w, y+h), (0, 255, 0), thickness=2)
                        xm = math.floor(x + w/2)
                        ym = math.floor(y + h/2)

                        # https://dev.intelrealsense.com/docs/projection-in-intel-realsense-sdk-20
                        dist = depth_frame.get_distance(xm, ym) 
                        face_point = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [xm, ym], dist)
                        cv2.putText(color_image, "{:.2f} {:.2f} {:.2f}".format(face_point[X],face_point[Y],face_point[Z]), (xm,ym), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )
                else :
                    face_point = [0,0, 0]

            rs_arucos = my_aruco.detect_and_draw(color_image)
            for rs_aruco in rs_arucos:
                id = rs_aruco['id']
                if id == 17:
                    pix_pos_a17 = tuple2int( rs_aruco['pos'] )
                    dist = depth_frame.get_distance(pix_pos_a17[X], pix_pos_a17[Y]) 
                    depth_a17 = rs.rs2_deproject_pixel_to_point(depth_intrinsics, pix_pos_a17, dist)
                    cv2.putText(color_image, "{:.2f} {:.2f} {:.2f}".format(depth_a17[X],depth_a17[Y],depth_a17[Z]), (pix_pos_a17[X], pix_pos_a17[Y]+30), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )

            if (ENABLE_RS_POINTCLOUD):
                point_image = my_pointcloud.handle_new_frame(depth_frame, color_frame, color_image)
                rs_image = np.hstack((color_image, depth_colormap, point_image))
            else:
                rs_image = np.hstack((color_image, depth_colormap))

            cv2.imshow('RealSense', rs_image)


    # ================
    # FONE CAM IMAGING
    if (ENABLE_FONE):
        ret, phone_frame = phone_cap.read()
        fone_arucos = my_aruco.detect_and_draw(phone_frame)
    
        # ================
        # Mirror center calibratoin
        mirror_fone_aruco_pix_pos_found = False
        hex_aruco_2_pixel_projection = MyFitProjection()
        # find and orden all arucos
        for fone_aruco in fone_arucos:
            id = fone_aruco['id']
            if id == 0:
                # https://cdn.inchcalculator.com/wp-content/uploads/2020/12/unit-circle-chart.png
                hex_aruco_2_pixel_projection.add_measurement((-0.5*math.sqrt(3),-0.5), fone_aruco['pos'])
            if id == 1:
                hex_aruco_2_pixel_projection.add_measurement((0,1), fone_aruco['pos'])
            if id == 2:
                hex_aruco_2_pixel_projection.add_measurement((0.5*math.sqrt(3),-0.5), fone_aruco['pos'])
            if id == 17:
                mirror_fone_aruco_pix_pos = fone_aruco['pos'] 
                mirror_fone_aruco_pix_pos_found = True
                cv2.drawMarker(phone_frame, mirror_fone_aruco_pix_pos, (255, 255, 255), cv2.MARKER_CROSS, 10, 1)
        # fit the model for mirror arucos
        if hex_aruco_2_pixel_projection.solve():
            # debug draw:
            hex_mirror_middle = tuple2int(hex_aruco_2_pixel_projection.evalX2Y((0,0)))
            x_ax  = tuple2int(hex_aruco_2_pixel_projection.evalX2Y((1,0)))
            y_ax  = tuple2int(hex_aruco_2_pixel_projection.evalX2Y((0,1)))
            cv2.line(phone_frame, hex_mirror_middle, x_ax, (255,0,255), 1)
            cv2.line(phone_frame, hex_mirror_middle, y_ax, (255,0,255), 1)


            # adjust mirror pos for calibration loop
            if calibration_loop and mirror_fone_aruco_pix_pos_found :
                delay_ms = cv2.getTrackbarPos('delay_ms', 'Parameters')

                mirror_center_aruco_pos = hex_aruco_2_pixel_projection.evalY2X(mirror_fone_aruco_pix_pos)
                cv2.putText(color_image, "{:.3f}:{:.3f} ".format(mirror_center_aruco_pos[X],mirror_center_aruco_pos[Y]), 
                    (mirror_fone_aruco_pix_pos[X],mirror_fone_aruco_pix_pos[Y]), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )

                if (time.perf_counter_ns() - calib_last_adjust_time_ns) > delay_ms*1000000:
                    calib_last_adjust_time_ns = time.perf_counter_ns()
                    print("{:.3f}:{:.3f} ".format(mirror_center_aruco_pos[X],mirror_center_aruco_pos[Y]))
                    
                    delta_x = mirror_center_aruco_pos[X]
                    delta_y = mirror_center_aruco_pos[Y]

                    print("{}".format(delta_x))
                    calib_mov_av[X].add_point(delta_x)
                    calib_mov_av[Y].add_point(delta_y)
                    if calib_mov_av[X].get_current() < 0.1 :
                        print("{}".format(my_serial.serial_write_and_read("o")))
                    elif calib_mov_av[X].get_current() > 0.1 : 
                        print("{}".format(my_serial.serial_write_and_read("l")))
                    if calib_mov_av[Y].get_current() < 0.1 :
                        print("{}".format(my_serial.serial_write_and_read("i")))
                    elif calib_mov_av[Y].get_current() > 0.1 : 
                        print("{}".format(my_serial.serial_write_and_read("p")))


    # Show images

    if ENABLE_FONE:
        cv2.imshow('Fone', phone_frame)

    # ==================
    #  interaction

    key = cv2.waitKey(1)
    if(key == ord('q') or key == ord('Q')):
        print("quiting")
        break
    elif (key == ord('o')):
        print("{}".format(my_serial.serial_write_and_read("o")))
    elif (key == ord('i')):
        print("{}".format(my_serial.serial_write_and_read("i")))
    elif (key == ord('p')):
        print("{}".format(my_serial.serial_write_and_read("p")))
    elif (key == ord('l')):
        print("{}".format(my_serial.serial_write_and_read("l")))
    elif (key == ord('O')):
        print("{}".format(my_serial.serial_write_and_read("O")))
    elif (key == ord('I')):
        print("{}".format(my_serial.serial_write_and_read("I")))
    elif (key == ord('P')):
        print("{}".format(my_serial.serial_write_and_read("P")))
    elif (key == ord('L')):
        print("{}".format(my_serial.serial_write_and_read("L")))
    elif (key == ord('1')):
        print("{}".format(my_serial.serial_write_and_read("1")))
    elif (key == ord('2')):
        print("{}".format(my_serial.serial_write_and_read("2")))      
    elif (key == ord('3')):
        print("{}".format(my_serial.serial_write_and_read("3")))
    elif (key == ord('4')):
        print("{}".format(my_serial.serial_write_and_read("4")))
    elif (key == ord('5')):
        print("{}".format(my_serial.serial_write_and_read("5")))  
    elif (key == ord('6')):
        print("{}".format(my_serial.serial_write_and_read("6")))

    elif False: # obsolete old scanning method
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

    elif (key == ord('c')):
        calibration_loop = not calibration_loop
        print(" calibration loop : {}".format(calibration_loop))
        enable_follow = False

    elif (key == ord('a') or key == ord('A')):
        mir_pos = my_serial.read_pos()
        if (face_point[2] > 0):
            data_str = "{:.0f},{:.0f},{:.3f}, {}".format(face_point[0], face_point[1], face_point[2], mir_pos)
            print( data_str )

    elif (key == ord('f')) :
        if not calibration_loop:
            enable_follow = not enable_follow
        print("enable folow {}".format(enable_follow))

    if calibration_loop :
        pass
        # OLD CALIBRATION LOOP
        # # move the mirror until done, then close the calib loop
        # if (time.perf_counter() - calib_step_start_time_s > 10 ) :
        #     calib_active_index += 1
        #     if (calib_active_index < len(calib_points)):
        #         point = calib_points[calib_active_index]
        #         serial_move(calib_points[calib_active_index])
        #         calib_step_start_time_s = time.perf_counter()
        #     else :
        #         calibration_loop = False
        #         with open(file_calib_json, 'w') as calib_file:
        #             json.dump(calib_results, calib_file, ensure_ascii=False, indent=4)

    if enable_follow:
        if (face_point[2] > 0) :
            set_mirror_angle = find_closest_mirror_angle(face_point)
            if (len(set_mirror_angle) > 0 ):
                my_serial.serial_move(set_mirror_angle)


#///////// 
# wrapup
print("Stop streaming")
cv2.destroyAllWindows()
my_serial.close()
# time.sleep(1)
# exit(0)
if (ENABLE_RS_FEED):
    pipeline.stop()
quit()

