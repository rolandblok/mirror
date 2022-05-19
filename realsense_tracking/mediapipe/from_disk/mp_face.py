import time

import cv2
import mediapipe as mp
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# For static images:
IMAGE_FILES = ['roland_kl.jpg']
with mp_face_detection.FaceDetection(
    model_selection=1, min_detection_confidence=0.5) as face_detection:
  for idx, file in enumerate(IMAGE_FILES):
    image = cv2.imread(file)
    tic = time.perf_counter()
    # Convert the BGR image to RGB and process it with MediaPipe Face Detection.
    no_times = 50
    for i in range(no_times):
        results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    toc = time.perf_counter()
    print(f"face duration {(toc - tic)/no_times:0.4f} seconds")

    # Draw face detections of each face.
    if not results.detections:
      continue
    annotated_image = image.copy()
    for detection in results.detections:
      print('Nose tip:')
      print(mp_face_detection.get_key_point(
          detection, mp_face_detection.FaceKeyPoint.NOSE_TIP))
      mp_drawing.draw_detection(annotated_image, detection)
    cv2.imwrite('annotated_image' + str(idx) + '.png', annotated_image)
