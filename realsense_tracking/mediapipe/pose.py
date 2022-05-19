import cv2
import mediapipe as mp
import os
if os.name == 'posix':
    import pyrealsense2.pyrealsense2 as rs
else:
    import pyrealsense2 as rs
import numpy as np

def emptyfunc(p):
    pass

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# https://www.analyticsvidhya.com/blog/2022/03/pose-detection-in-image-using-mediapipe-library/

# camera = '../videos/video.avi'
# camera = '../videos/video_1440_1440.mp4'
camera = '../videos/video_1440_1440_zoomed.mp4'
# camera = 'realsense'
if (camera == 'realsense'):
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))
    print(device_product_line)

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)

    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    # config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 6)
    # Start streaming
    pipeline.start(config)
    frame_nr = 0
else:
    cap = cv2.VideoCapture(camera)
    cv2.namedWindow('Parameters', cv2.WINDOW_AUTOSIZE)
    cv2.resizeWindow('Parameters', 1000, 200)
    cv2.createTrackbar('frame_nr', 'Parameters', 1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), emptyfunc)

with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5, 
    model_complexity=0) as pose:
   while (True):
    if (camera == 'realsense'):
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        # success, image = cap.read()
        # if not success:
        #     print("Ignoring empty camera frame.")
        #     # If loading a video, use 'break' instead of 'continue'.
        #     continue.
        if not color_frame:
            continue
        # Convert images to numpy arrays
        image = np.asanyarray(color_frame.get_data())
    else:
        frame_nr_params = cv2.getTrackbarPos('frame_nr', 'Parameters')
        frame_nr = cap.get(cv2.CAP_PROP_POS_FRAMES)
        if (frame_nr != frame_nr_params ):
            cap.set(1,frame_nr_params)

        success, image = cap.read()

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    # Draw the pose annotation on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
    # Flip the image horizontally for a selfie-view display.
    if camera != 'realsense':
        frame_nr = cap.get(cv2.CAP_PROP_POS_FRAMES)
        cv2.setTrackbarPos('frame_nr', 'Parameters', int(frame_nr))
    else:
        frame_nr += 1
    cv2.putText(image, "{:.0f} ".format(frame_nr), (10,10), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (255,255,255), thickness=2 )

    cv2.imshow('MediaPipe Pose', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("Stop streaming")
cv2.destroyAllWindows()
if (camera == 'realsense'):
    pipeline.stop()
quit()