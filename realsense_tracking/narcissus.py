
###############################################
##      MiRROR MaNaAgeR       ##
###############################################

from doctest import FAIL_FAST

from cv2 import floodFill
from my_utils import *
from fone_cam import *
from my_aruco import *
from my_pointcloud import *
from my_serial import *
from my_mirror_calib import *
from my_face_detector import *

import json
import time, math, os.path
import pyrealsense2 as rs
import numpy as np
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

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
ENABLE_RS_POINTCLOUD = False
ENABLE_FACE_DETECTION = DetectorType.FACE_DETECTION_MEDIAPIPE
# ENABLE_FACE_DETECTION = DetectorType.FACE_DETECTION_HAAR
# ENABLE_FACE_DETECTION = DetectorType.FACE_DETECTION_DLIB
ENABLE_ARUCO_DETECTION = True
ENABLE_SERIAL = True

STREAM_WIDTH=640
STREAM_HEIGHT=480

MIRROR_ARUCO_RADIUS = 0.15 # meters
FACE_FOLLOW_IDLE_TIME_NS = 2e9 # (n)seconds
CALIBRATION_MIRROR = 0
NO_MIRRORS = 8
#    2 1
# 7 3 C 0 6
#    4 5


class FollowMode(Enum):
    DISABLE = 0
    CALIBRATE = 1
    MONO = 2
    DUO = 3

# init globalsss 
file_calib_json = 'calib_pos.json'
follow_mode = FollowMode.DISABLE
calib_points = []     # array [[:camera-xyz][:mirror-angles] :for all calib points]
calib_active_index = 0
calib_step_start_time_s = 0
calib_last_adjust_time_ns = time.perf_counter_ns()
face_follow_last_adjust_time_ns = time.perf_counter_ns()
my_mirror_calib = MyMirrorCalib()
if os.path.exists(file_calib_json) :
    with open(file_calib_json, 'r') as calib_file:
        calib_results = json.load(calib_file)
        for calib_point in calib_results:
            angles = []
            angles.append( (calib_point[1][0]) * math.pi / 180)
            angles.append( (calib_point[1][1]) * math.pi / 180)
            my_mirror_calib.add_data(calib_point[0], angles )

        if False:  # debug plot input data
            if len(calib_results) > 0:
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                for calib_point in calib_results:
                    ax.scatter(calib_point[0][X], calib_point[0][Y], calib_point[0][Z])
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
                plt.show() 

        res = my_mirror_calib.solve()
        if (res):
            my_mirror_calib.printCalibMatrix()
            my_mirror_calib.printResiduals()
            my_mirror_calib.printResidualsStatistics()
        else : 
            print('fit failed')
else :
    calib_results = []
    MyMirrorCalib = 0

  

mouse_btns = [False, False, False]
mouse_prev = [0, 0]

my_aruco = MyAruco()

my_fps_rs = MyFPS(30)
my_fps_phone = MyFPS(30)

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
        
# ========================
# open window and callbacks
cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
cv2.moveWindow("RealSense", 20, 20)
cv2.namedWindow('Fone', cv2.WINDOW_AUTOSIZE)
cv2.moveWindow("Fone", 20, 660)
cv2.setMouseCallback('RealSense', my_mouse)
cv2.namedWindow('Parameters', cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow('Parameters', 1000, 200)
cv2.createTrackbar('delay_ms', 'Parameters', 200, 1000, empty_fun)

if ENABLE_RS_POINTCLOUD and ENABLE_RS_FEED:
    my_pointcloud = MyPointCloud()
    my_pointcloud.start(pipeline)

if (ENABLE_FONE):
    # open the fone camera feed
    phone_cap = VideoCapture(CAMERA_IP)
    if not phone_cap.isOpened():
        print("no fone camerag ")
        ENABLE_FONE = False


my_face_detector = MyFaceDetector(ENABLE_FACE_DETECTION)



while ENABLE_FONE or ENABLE_RS_FEED:

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

            if not follow_mode == FollowMode.CALIBRATE:
                eye_centers = my_face_detector.detect(color_image, color_image_disp)
                for eye_center in eye_centers:
                    # https://dev.intelrealsense.com/docs/projection-in-intel-realsense-sdk-20
                    dist = depth_frame.get_distance(eye_center[X], eye_center[Y]) 
                    face_3Dpoint = rs.rs2_deproject_pixel_to_point(depth_intrinsics, eye_center, dist)
                    face_3Dpoints.append(face_3Dpoint)
                    cv2.putText(color_image_disp, "{:.2f} {:.2f} {:.2f}".format(face_3Dpoint[X],face_3Dpoint[Y],face_3Dpoint[Z]), 
                                eye_center, cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )
                    cv2.drawMarker(color_image_disp, eye_center, (255, 255, 255), cv2.MARKER_CROSS, 10, 1)


            if (ENABLE_ARUCO_DETECTION):
                rs_arucos = my_aruco.detect_and_draw(color_image, color_image_disp)
                for rs_aruco in rs_arucos:
                    id = rs_aruco['id']
                    if id == 17:
                        pix_pos_a17 = tuple2int( rs_aruco['pos'] )
                        dist = depth_frame.get_distance(pix_pos_a17[X], pix_pos_a17[Y]) 
                        depth_a17_found = True
                        depth_a17 = rs.rs2_deproject_pixel_to_point(depth_intrinsics, pix_pos_a17, dist)
                        
                        cv2.putText(color_image_disp, "{:.2f} {:.2f} {:.2f}".format(depth_a17[X],depth_a17[Y],depth_a17[Z]), (pix_pos_a17[X], pix_pos_a17[Y]+30), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )

            cv2.putText(color_image_disp, "FPS {:.1f}".format(my_fps_rs.get_fps()), (20, 40), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )

            if (ENABLE_RS_POINTCLOUD):
                point_image = my_pointcloud.handle_new_frame(depth_frame, color_frame, color_image)
                rs_image = np.hstack((color_image_disp, depth_colormap, point_image))
            else:
                rs_image = np.hstack((color_image_disp, depth_colormap))

            cv2.imshow('RealSense', rs_image)


    # ================
    # FONE CAM IMAGING
    if (ENABLE_FONE):
        ret, phone_frame = phone_cap.read()
        phone_frame_disp = phone_frame.copy()
        my_fps_phone.add_frame()

        fone_arucos = my_aruco.detect_and_draw(phone_frame, phone_frame_disp)
    
        # ================
        # Mirror center calibratoin
        mirror_fone_a17_pix_pos_found = False
        hex_aruco_2_pixel_projection = MyFitProjection()
        # find and orden all arucos
        for fone_aruco in fone_arucos:
            id = fone_aruco['id']
            if id == 0:
                # https://cdn.inchcalculator.com/wp-content/uploads/2020/12/unit-circle-chart.png
                hex_aruco_2_pixel_projection.add_measurement((0.5*MIRROR_ARUCO_RADIUS,-0.5*MIRROR_ARUCO_RADIUS*math.sqrt(3)), fone_aruco['pos'])
            elif id == 1:
                hex_aruco_2_pixel_projection.add_measurement((-MIRROR_ARUCO_RADIUS, 0), fone_aruco['pos'])
            elif id == 2:
                hex_aruco_2_pixel_projection.add_measurement((0.5*MIRROR_ARUCO_RADIUS,+0.5*MIRROR_ARUCO_RADIUS*math.sqrt(3)), fone_aruco['pos'])
            # if id == 0:
            #     # https://cdn.inchcalculator.com/wp-content/uploads/2020/12/unit-circle-chart.png
            #     hex_aruco_2_pixel_projection.add_measurement((-0.5*MIRROR_ARUCO_RADIUS*math.sqrt(3),-0.5*MIRROR_ARUCO_RADIUS), fone_aruco['pos'])
            # if id == 1:
            #     hex_aruco_2_pixel_projection.add_measurement((0,MIRROR_ARUCO_RADIUS), fone_aruco['pos'])
            # if id == 2:
            #     hex_aruco_2_pixel_projection.add_measurement((0.5*MIRROR_ARUCO_RADIUS*math.sqrt(3),-0.5*MIRROR_ARUCO_RADIUS), fone_aruco['pos'])
            elif id == 17:
                mirror_fone_a17_pix_pos = fone_aruco['pos'] 
                mirror_fone_a17_pix_pos_found = True
                cv2.drawMarker(phone_frame_disp, mirror_fone_a17_pix_pos, (255, 255, 255), cv2.MARKER_CROSS, 10, 1)

        # fit the model for mirror arucos
        if hex_aruco_2_pixel_projection.solve():
            # debug draw an axis over the mirror, of 10 centumeters:
            hex_mirror_middle = tuple2int(hex_aruco_2_pixel_projection.evalX2Y((0,0)))
            x_ax  = tuple2int(hex_aruco_2_pixel_projection.evalX2Y((0.10, 0   )))
            y_ax  = tuple2int(hex_aruco_2_pixel_projection.evalX2Y((0,    0.10)))
            cv2.line(phone_frame_disp, hex_mirror_middle, x_ax, (255,0,255), 2)
            cv2.line(phone_frame_disp, hex_mirror_middle, y_ax, (255,0,255), 2)


        # adjust mirror pos for calibration loop
        if hex_aruco_2_pixel_projection.solved and mirror_fone_a17_pix_pos_found:
            mirror_center_a17_pos = hex_aruco_2_pixel_projection.evalY2X(mirror_fone_a17_pix_pos)
            cv2.putText(phone_frame_disp, "{:.3f}:{:.3f} ".format(mirror_center_a17_pos[X], mirror_center_a17_pos[Y]), 
                (mirror_fone_a17_pix_pos[X],mirror_fone_a17_pix_pos[Y]), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )


            if (follow_mode == FollowMode.CALIBRATE) and depth_a17_found:

                delay_ms = cv2.getTrackbarPos('delay_ms', 'Parameters')
                if (time.perf_counter_ns() - calib_last_adjust_time_ns) > delay_ms*1000000:
                    calib_last_adjust_time_ns = time.perf_counter_ns()
                    
                    d_angle_x = math.atan(mirror_center_a17_pos[X] / depth_a17[Z]) * 360/math.pi 
                    d_angle_y = math.atan(mirror_center_a17_pos[Y] / depth_a17[Z]) * 360/math.pi 

                    if round(d_angle_x) == 0 and round(d_angle_y) == 0 :
                        angle_pos = my_serial.read_pos(CALIBRATION_MIRROR)
                        calib_results.append([depth_a17, angle_pos])
                        print(" adding {} : {})".format(depth_a17, angle_pos))
                    else:
                        my_serial.serial_delta_move(CALIBRATION_MIRROR, d_angle_x,-d_angle_y)



    # Show images

    if ENABLE_FONE:
        cv2.putText(phone_frame_disp, "FPS {:.1f}".format(my_fps_phone.get_fps()), (20, 40), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )

        cv2.imshow('Fone', phone_frame_disp)

    # face following
    if (follow_mode != FollowMode.DISABLE) and (my_mirror_calib.solved):
        if (follow_mode == FollowMode.MONO) and len(face_3Dpoints) > 0:
                face_follow_last_adjust_time_ns = time.perf_counter_ns()
                angles = my_mirror_calib.eval(face_3Dpoints[0])
                angles_deg = [180 * a / math.pi for a in angles ]
                angles_deg[0], angles_deg[1] = angles_deg[1], angles_deg[0]
                
                my_serial.serial_move(CALIBRATION_MIRROR, angles_deg)
        elif (follow_mode == FollowMode.DUO) and len(face_3Dpoints) > 1:
                face_follow_last_adjust_time_ns = time.perf_counter_ns()
                angles0 = my_mirror_calib.eval(face_3Dpoints[0])
                angles1 = my_mirror_calib.eval(face_3Dpoints[1])
                angles_deg0 = [180 * a / math.pi for a in angles0 ]
                angles_deg1 = [180 * a / math.pi for a in angles1 ]
                angles_deg_av = np.mean( np.array([ angles_deg0, angles_deg1 ]), axis=0 )

                angles_deg_av[0], angles_deg[1] = angles_deg[1], angles_deg[0]
                my_serial.serial_move(CALIBRATION_MIRROR, angles_deg_av)
        elif time.perf_counter_ns() - face_follow_last_adjust_time_ns > FACE_FOLLOW_IDLE_TIME_NS:
            face_follow_last_adjust_time_ns = time.perf_counter_ns()
            angles_deg = [0,0]
            my_serial.serial_move(CALIBRATION_MIRROR, angles_deg)


    # ==================
    #  interaction

    key = cv2.waitKey(1)
    if key == -1:
        pass
    elif(key == ord('q') or key == ord('Q')):
        print("quiting")
        break
    elif (key == ord('o')):
        print("{}".format(my_serial._serial_write_and_read("o")))
    elif (key == ord('i')):
        print("{}".format(my_serial._serial_write_and_read("i")))
    elif (key == ord('p')):
        print("{}".format(my_serial._serial_write_and_read("p")))
    elif (key == ord('l')):
        print("{}".format(my_serial._serial_write_and_read("l")))
    elif (key == ord('O')):
        print("{}".format(my_serial._serial_write_and_read("O")))
    elif (key == ord('I')):
        print("{}".format(my_serial._serial_write_and_read("I")))
    elif (key == ord('P')):
        print("{}".format(my_serial._serial_write_and_read("P")))
    elif (key == ord('L')):
        print("{}".format(my_serial._serial_write_and_read("L")))
    elif (key == ord('1')):
        print("{}".format(my_serial._serial_write_and_read("1")))
    elif (key == ord('2')):
        print("{}".format(my_serial._serial_write_and_read("2")))      
    elif (key == ord('3')):
        print("{}".format(my_serial._serial_write_and_read("3")))
    elif (key == ord('4')):
        print("{}".format(my_serial._serial_write_and_read("4")))
    elif (key == ord('5')):
        print("{}".format(my_serial._serial_write_and_read("5")))  
    elif (key == ord('6')):
        print("{}".format(my_serial._serial_write_and_read("6")))

    elif (key == ord('c')):
        if follow_mode == FollowMode.CALIBRATE:  # dump the data
            with open(file_calib_json, 'w') as calib_file:
                json.dump(calib_results, calib_file, ensure_ascii=False, indent=4)
            follow_mode = FollowMode.DISABLE
        else:
            follow_mode = FollowMode.CALIBRATE
        print("caribation loop {}".format(follow_mode))

    elif (key == ord('s')) : 
        if follow_mode != FollowMode.CALIBRATE:
            follow_mode = FollowMode.DISABLE
        print("enable follow {}".format(follow_mode))
    elif (key == ord('f')) :
        if follow_mode != FollowMode.CALIBRATE:
            follow_mode = FollowMode.MONO
        print("enable follow {}".format(follow_mode))
    elif (key == ord('g')) :
        if follow_mode != FollowMode.CALIBRATE:
            follow_mode = FollowMode.DUO
        print("enable follow {}".format(follow_mode))

    else :
        print(chr(key) + " pressed, unknow command")
        print(" q : quit")
        print(" s : stop follow")
        print(" f : follow mono")
        print(" g : follow duo")
        print(" c : calibration (need to press c again to safe calibration data!)")
        print(" I i p P : left / right")
        print(" O o l L : up / down")

    


#///////// 
# wrapup
print("Stop streaming")
cv2.destroyAllWindows()
my_serial.close()
my_face_detector.close()
# time.sleep(1)
# exit(0)
if (ENABLE_RS_FEED):
    pipeline.stop()

