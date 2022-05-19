# mirror
Narcissus

Moving a hex mirror to look you in the face.

Moving a hex mirror to make you smile at a friend.

# install raspberry
use rapbian (buster) :   cat /etc/os-release

Let op: het lukt om mediapipe te installeerne op eenvoudige manier, als realsense er nog niet is.

media pipe : https://pypi.org/project/mediapipe-rpi4/
    sudo apt install ffmpeg python3-opencv python3-pip
    sudo apt install libxcb-shm0 libcdio-paranoia-dev libsdl2-2.0-0 libxv1  libtheora0 libva-drm2 libva-x11-2 libvdpau1 libharfbuzz0b libbluray2 libatlas-base-dev libhdf5-103 libgtk-3-0 libdc1394-22 libopenexr23
            pip install mediapipe-rpi4
    DO NIET DE PIP MET SUDO


realsense : https://github.com/datasith/Ai_Demos_RPi/wiki/Raspberry-Pi-4-and-Intel-RealSense-D435
    ssl   : sudo apt-get install libssl-dev
    als we nu eens niet all die protobug doen enzo... : DAN WERKT HET!
        Let op : in  /home/pi/.local/lib/python3.7/site-packages
            staat dat we doen :  protobuf-3.20.1.dist-info

numpy : pip3 install -U numpy

Everything python3
Het is handig om de link van python om te zetten naar python 3

samba : https://tutorials-raspberrypi.com/raspberry-pi-samba-server-share-files-in-the-local-network/
        https://linoxide.com/how-to-add-samba-user-linux/
        [share]
            Comment = narcissus2_share
            Path = /home/pi/share
            valid users = roland, pi
            Browseable = yes
            Writeable = Yes
            only guest = no
            create mask = 0777
            directory mask = 0777
            Public = yes
            Guest ok = no



# used library
stolen (forked)  libs : https://www.arduino.cc/reference/en/libraries/servosmooth/
