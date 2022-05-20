
###############################################
##      MiRROR MaNaAgeR       ##
###############################################

from doctest import FAIL_FAST

from my_utils import *
from my_serial import *
from my_mirror_move import *
from my_face_detector import *
from my_camera_to_mirror import *

import json
import time, math, os.path
import numpy as np

import os
if os.name == 'posix':
    import pyrealsense2.pyrealsense2 as rs
else:
    import pyrealsense2 as rs

import cv2
print("opencv version : " + cv2.__version__ )

WERKPLAATS = True
if WERKPLAATS:
    if os.name == 'posix':
        COM_PORT = '/dev/ttyUSB0'
        RS_REFRESH = 15
    else:
        COM_PORT = "COM10"
        RS_REFRESH = 15
else: 
    COM_PORT = "COM4"

ENABLE_RS_FEED = True
ENABLE_FACE_DETECTION = DetectorType.FACE_DETECTION_MEDIAPIPE
ENABLE_SERIAL = True
ENBALE_SCREEN = True

STREAM_WIDTH=640
STREAM_HEIGHT=480

FACE_FOLLOW_IDLE_TIME_NS = 2e9 # (n)seconds
NO_MIRRORS = 8
#    2 1
# 7 3 C 0 6
#    4 5

class FollowMode(Enum):
    DISABLE = 0
    MONO = 1
    DUO = 2
    DYNAMIC = 3

# init globalsss 
file_calib_json = 'calib_pos.json'
follow_mode = FollowMode.DISABLE
face_follow_last_adjust_time_ns = time.perf_counter_ns()
glb_active_mirror = 0
glb_active_mirror_cur_angles = [0,0]

my_camera_to_mirror = MyCameraToMirror()

mouse_btns = [False, False, False]
mouse_prev = [0, 0]

keyboard_mirror_selection_active = False

my_fps_rs = MyFPS(30)
my_fps_phone = MyFPS(30)

# =================
# SERIAL ENABLING

if ENABLE_SERIAL:
    my_serial = MyMirrorSerial(COM_PORT)
else:
    my_serial = MyMirrorSerial("")
my_mirror_move = MyMirrorMove(my_serial)

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
    config.enable_stream(rs.stream.depth, STREAM_WIDTH, STREAM_HEIGHT, rs.format.z16, RS_REFRESH)
    config.enable_stream(rs.stream.color, STREAM_WIDTH, STREAM_HEIGHT, rs.format.bgr8, RS_REFRESH)
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
            pass
        elif mouse_btns[1]:
            pass
        elif mouse_btns[2]:
            pass
        
# ========================
# open window and callbacks
if ENBALE_SCREEN:
    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow("RealSense", 20, 20)
    cv2.setMouseCallback('RealSense', my_mouse)
    cv2.namedWindow('Parameters', cv2.WINDOW_AUTOSIZE)
    cv2.resizeWindow('Parameters', 1000, 200)
    cv2.createTrackbar('delay_ms', 'Parameters', 200, 1000, empty_fun)

my_face_detector = MyFaceDetector(ENABLE_FACE_DETECTION)

while ENABLE_RS_FEED or ENABLE_SERIAL:

    # ================
    # Realsense imaging
    depth_a17_found = False
    face_3Dpoints = []
    if (ENABLE_RS_FEED):
        frameset = pipeline.poll_for_frames()
        if frameset.size() > 0:
            depth_frame = frameset.get_depth_frame()
            color_frame = frameset.get_color_frame()
            if not depth_frame or not color_frame:
                continue
            my_fps_rs.add_frame()

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_image_disp = color_image.copy()
            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = color_image.shape

            eye_centers = my_face_detector.detect(color_image, color_image_disp)
            for eye_center in eye_centers:
                # https://dev.intelrealsense.com/docs/projection-in-intel-realsense-sdk-20
                try:
                    dist = depth_frame.get_distance(eye_center[X], eye_center[Y]) 
                except:
                    # print(f"dist not calculated for {eye_center[X]} { eye_center[Y]}")
                    dist = 0
                if dist > 0:
                    face_3Dpoint = rs.rs2_deproject_pixel_to_point(depth_intrinsics, eye_center, dist)
                    face_3Dpoints.append(face_3Dpoint)
                    cv2.putText(color_image_disp, "{:.2f} {:.2f} {:.2f}".format(face_3Dpoint[X],face_3Dpoint[Y],face_3Dpoint[Z]), 
                                eye_center, cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )
                    cv2.drawMarker(color_image_disp, eye_center, (255, 255, 255), cv2.MARKER_CROSS, 10, 1)


            cv2.putText(color_image_disp, "FPS {:.1f}".format(my_fps_rs.get_fps()), (20, 40), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )
            if len(face_3Dpoints) > 0:
                cv2.putText(color_image_disp, "FACE {:.2f},{:.2f},{:.2f}".format(face_3Dpoints[0][X],face_3Dpoints[0][Y],face_3Dpoints[0][Z]), (20, 70), cv2.FONT_HERSHEY_SIMPLEX , 1, (100,100,255), thickness=2 )
                mir_angles = my_camera_to_mirror.get_angle(glb_active_mirror, face_3Dpoints[0])
                cv2.putText(color_image_disp, "FMI {} : {:.2f},{:.2f}".format(glb_active_mirror,mir_angles[0], mir_angles[1]), (20, 100), cv2.FONT_HERSHEY_SIMPLEX , 1, (100,100,255), thickness=2 )
            cv2.putText(color_image_disp, "MIR {} : {:.2f},{:.2f}".format(glb_active_mirror,glb_active_mirror_cur_angles[0], glb_active_mirror_cur_angles[1]), (20, 130), cv2.FONT_HERSHEY_SIMPLEX , 1, (100,100,255), thickness=2 )

            rs_image = np.hstack((color_image_disp, depth_colormap))
            if ENBALE_SCREEN:
                cv2.imshow('RealSense', rs_image)

    # face following
    # if (follow_mode != FollowMode.DISABLE) and (my_mirror_calib.solved):
    if follow_mode != FollowMode.DISABLE :
        if (follow_mode == FollowMode.MONO) and len(face_3Dpoints) > 0:
                face_follow_last_adjust_time_ns = time.perf_counter_ns()
                # angles = my_mirror_calib.eval(face_3Dpoints[0])
                # angles_deg = [180 * a / math.pi for a in angles ]
                # print(f"    {face_3Dpoints[0]=} {angles_deg=}")
                # angles_deg[0], angles_deg[1] = angles_deg[1], angles_deg[0]
                for m in range(NO_MIRRORS):
                    angles = my_camera_to_mirror.get_angle(m, face_3Dpoints[0])
                    my_mirror_move.move(m, angles)

        elif (follow_mode == FollowMode.DUO) and len(face_3Dpoints) > 1:
                face_follow_last_adjust_time_ns = time.perf_counter_ns()
                # angles0 = my_mirror_calib.eval(face_3Dpoints[0])
                # angles1 = my_mirror_calib.eval(face_3Dpoints[1])
                # angles_deg0 = [180 * a / math.pi for a in angles0 ]
                # angles_deg1 = [180 * a / math.pi for a in angles1 ]
                # angles_deg_av[0], angles_deg[1] = angles_deg[1], angles_deg[0]
                for m in range(NO_MIRRORS):
                    angles_deg0 = my_camera_to_mirror.get_angle(m, face_3Dpoints[0])
                    angles_deg1 = my_camera_to_mirror.get_angle(m, face_3Dpoints[1])
                    angles_av = np.mean( np.array([ angles_deg0, angles_deg1 ]), axis=0 )

                    my_mirror_move.move(m, angles_av)
        elif (follow_mode == FollowMode.DYNAMIC): 
            if len(face_3Dpoints) > 1:
                face_follow_last_adjust_time_ns = time.perf_counter_ns()
                for m in range(NO_MIRRORS):
                    angles_deg0 = my_camera_to_mirror.get_angle(m, face_3Dpoints[0])
                    angles_deg1 = my_camera_to_mirror.get_angle(m, face_3Dpoints[1])
                    angles_av = np.mean( np.array([ angles_deg0, angles_deg1 ]), axis=0 )

                    my_mirror_move.move(m, angles_av)
        elif time.perf_counter_ns() - face_follow_last_adjust_time_ns > FACE_FOLLOW_IDLE_TIME_NS:
            face_follow_last_adjust_time_ns = time.perf_counter_ns()
            for m in range(NO_MIRRORS):
                my_mirror_move.move(m, [0,0])


    # ==================
    #  interaction

    key = cv2.waitKey(1)
    if key == -1:
        pass
    elif(key == ord('q') or key == ord('Q')):
        print("quiting")
        break
    elif (keyboard_mirror_selection_active):    
        if ((key == ord('0')) or (key == ord('1')) or (key == ord('2')) or (key == ord('3')) or 
            (key == ord('4')) or (key == ord('5')) or (key == ord('6'))  or (key == ord('7'))   ) :
            glb_active_mirror = int(chr(key))
            my_serial._serial_write(f"m,{glb_active_mirror}")
            glb_active_mirror_cur_angles = my_mirror_move.read_angles(glb_active_mirror)
        keyboard_mirror_selection_active = False
    elif (key == ord('o')):
        print("{}".format(my_serial._serial_write_and_read("o")))
        glb_active_mirror_cur_angles = my_mirror_move.read_angles(glb_active_mirror)
    elif (key == ord('i')):
        print("{}".format(my_serial._serial_write_and_read("i")))
        glb_active_mirror_cur_angles = my_mirror_move.read_angles(glb_active_mirror)
    elif (key == ord('p')):
        print("{}".format(my_serial._serial_write_and_read("p")))
        glb_active_mirror_cur_angles = my_mirror_move.read_angles(glb_active_mirror)
    elif (key == ord('l')):
        print("{}".format(my_serial._serial_write_and_read("l")))
        glb_active_mirror_cur_angles = my_mirror_move.read_angles(glb_active_mirror)
    elif (key == ord('O')):
        print("{}".format(my_serial._serial_write_and_read("O")))
        glb_active_mirror_cur_angles = my_mirror_move.read_angles(glb_active_mirror)
    elif (key == ord('I')):
        print("{}".format(my_serial._serial_write_and_read("I")))
        glb_active_mirror_cur_angles = my_mirror_move.read_angles(glb_active_mirror)
    elif (key == ord('P')):
        print("{}".format(my_serial._serial_write_and_read("P")))
        glb_active_mirror_cur_angles = my_mirror_move.read_angles(glb_active_mirror)
    elif (key == ord('L')):
        print("{}".format(my_serial._serial_write_and_read("L")))
        glb_active_mirror_cur_angles = my_mirror_move.read_angles(glb_active_mirror)
    elif (key == ord('1')):
        glb_active_mirror_cur_angles = (-10,-10)
        my_mirror_move.move(glb_active_mirror, glb_active_mirror_cur_angles)
    elif (key == ord('2')):
        glb_active_mirror_cur_angles = (0,-10)
        my_mirror_move.move(glb_active_mirror, glb_active_mirror_cur_angles)
    elif (key == ord('3')):
        glb_active_mirror_cur_angles = (10, -10)
        my_mirror_move.move(glb_active_mirror, glb_active_mirror_cur_angles)
    elif (key == ord('4')):
        glb_active_mirror_cur_angles = (-10,0)
        my_mirror_move.move(glb_active_mirror, glb_active_mirror_cur_angles)
    elif (key == ord('5')):
        glb_active_mirror_cur_angles = (0,0)
        my_mirror_move.move(glb_active_mirror, glb_active_mirror_cur_angles)
    elif (key == ord('6')):
        glb_active_mirror_cur_angles = (10,0)
        my_mirror_move.move(glb_active_mirror, glb_active_mirror_cur_angles)
    elif (key == ord('7')):
        glb_active_mirror_cur_angles = (-10,10)
        my_mirror_move.move(glb_active_mirror, glb_active_mirror_cur_angles)
    elif (key == ord('8')):
        glb_active_mirror_cur_angles = (0,10)
        my_mirror_move.move(glb_active_mirror, glb_active_mirror_cur_angles)
    elif (key == ord('9')):
        glb_active_mirror_cur_angles = (10,10)
        my_mirror_move.move(glb_active_mirror, glb_active_mirror_cur_angles)
    elif (key == ord('z')):
        my_mirror_move.zero(glb_active_mirror)
        my_mirror_move.save()
    elif (key == ord('x')):
        my_mirror_move.scale(glb_active_mirror, (10,10))
        my_mirror_move.save()
    elif (key == ord('v')):
        if (len(face_3Dpoint) > 0):
            my_camera_to_mirror.zero_angle(glb_active_mirror, glb_active_mirror_cur_angles, face_3Dpoints[0])
            my_camera_to_mirror.save()
        else:
            print("no zero, no face detected")
    elif (key == ord('m')):
        print("mirror selection active")
        keyboard_mirror_selection_active = True

    elif (key == ord('s')) : 
        follow_mode = FollowMode.DISABLE
        glb_active_mirror_cur_angles = [0,0]
        for m in range(NO_MIRRORS):
            my_mirror_move.move(m, glb_active_mirror_cur_angles)
        print("enable follow {}".format(follow_mode))
    elif (key == ord('f')) :
        follow_mode = FollowMode.MONO
        print("enable follow {}".format(follow_mode))
    elif (key == ord('g')) :
        follow_mode = FollowMode.DUO
        print("enable follow {}".format(follow_mode))
    elif (key == ord('h')) :
        follow_mode = FollowMode.DYNAMIC
        print("enable follow {}".format(follow_mode))

    else :
        print(chr(key) + " pressed, unknow command")
        print(" q : quit")
        print(" s : stop follow")
        print(" f : follow mono")
        print(" g : follow duo")
        print(" 123456789 : set active mirror to angle")
        print(" I i p P : left / right")
        print(" O o l L : up / down")
        print(" m 01234567: select mirror n" )
        print(" z : zero the active mirror angle" )
        print(" x : set active mirror scale to 10 degrees (use angle meter phone)" )
        print(" v : zero active mirror to your face")

    


#///////// 
# wrapup
print("Stop streaming")
if ENBALE_SCREEN:
    cv2.destroyAllWindows()
my_serial.close()
my_face_detector.close()
# time.sleep(1)
# exit(0)
if (ENABLE_RS_FEED):
    pipeline.stop()

