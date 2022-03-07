

import cv2
import queue, threading
from my_utils import *

# bufferless VideoCapture
# https://stackoverflow.com/questions/54460797/how-to-disable-buffer-in-opencv-camera
class VideoCapture:

  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()   # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      dat = {'ret':ret, 'frame':frame}  
      self.q.put(dat)

  def read(self):
    dat = self.q.get()
    return dat['ret'], dat['frame']
  def get(self, arg):
    return self.cap.get(arg)
  def isOpened(self):
    return self.cap.isOpened()


class FoneCam:
    def __init__(self, record = False):

        # ========================
        # open window and callbacks
        cv2.namedWindow('fone_cam', cv2.WINDOW_AUTOSIZE)
        # out = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'XVID'), 25, get_dims(cap, res))
        my_fps_phone = MyFPS(30)

        phone_cap = VideoCapture("http://192.168.94.22:4747/video")
        if record:
          fps = phone_cap.get(cv2.CAP_PROP_FPS)
          res = (int(phone_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(phone_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
          out = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'MPEG'), fps, res)

        while True:
            my_fps_phone.add_frame()
            ret, phone_frame = phone_cap.read()
            if record:
              out.write(phone_frame)

            cv2.putText(phone_frame, "FPS {:.1f}".format(my_fps_phone.get_fps()), (20, 40), cv2.FONT_HERSHEY_SIMPLEX , 1, (255,255,255), thickness=2 )
            cv2.imshow('fone_cam', phone_frame)


            key = cv2.waitKey(1)
            if(key == ord('q') or key == ord('Q')):
                print("quiting")
                break



        # wrapup
        print("Stop streaming")
        if record :
          out.release()
        cv2.destroyAllWindows()
        # time.sleep(1)
        # exit(0)
        quit()


# ===========================
#  TESTING
# ===========================
if __name__ == '__main__':
  phone_cap = FoneCam(True)
