#!/usr/bin/env python3
"""
SYNOPSIS

    seer.py [-h,--help] [-v,--verbose] [--version]

DESCRIPTION

    This is a tool that will watch the output of a video camera. It will
    highlight any movement that it sees. It also detects the relative amount of
    motion and stillnes and indicates significant changes on stdout.
    During period of movement the individual camera frames will be saved.

    THIS IS A ROUGH DRAFT. EVERYTHING WORKS.

    On OS X:
        brew tap homebrew/science
        brew install opencv  # or, "brew install opencv --env=std"
        export PYTHONPATH=/usr/local/lib/python2.7/site-packages:${PYTHONPATH}

    Video playback on OS X:
        brew install mplayer  # takes a long time (~ 5 minutes)
        brew install mencoder
        mplayer -vo corevideo "mf://movement*.png" -mf type=png:fps=30 -loop 0

    Video encoding on OS X:
        mencoder "mf://*.png" -mf type=png:fps=25 -ovc lavc -lavcopts vcodec=mpeg4 -o output.mov

    This docstring will be printed by the script if there is an error or
    if the user requests help (-h or --help).

EXAMPLES

    The following are some examples of how to use this script.
    $ movement.py --version
    1

EXIT STATUS

    This exits with status 0 on success and 1 otherwise.
    This exits with a status greater than 1 if there was an
    unexpected run-time error.

AUTHOR

    Noah Spurrier <noah@noah.org>

LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2019, Noah Spurrier
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

VERSION

    Version 8
"""

__version__ = "Version 8"
__date__ = "Mon Feb 11 14:42:15 PST 2019"
__author__ = "Noah Spurrier <noah@noah.org>"

import sys
import os
import traceback
import optparse
import time
from datetime import datetime
import logging
import time
import cv2
import numpy

#DELTA_COUNT_THRESHOLD = 2000
DELTA_FACTOR_THRESHOLD = 0.2
CAM_RES_X = 640
CAM_RES_Y = 480
# CAM_RES_X = 1280
# CAM_RES_Y = 720
CAM_PIXEL_COUNT = float(CAM_RES_X * CAM_RES_Y)
DELTA_FACTOR_THRESHOLD = 0.25  # DELTA_COUNT_THRESHOLD/float(CAM_PIXEL_COUNT)


def open_camera(camera_number=0):
    ###    #for cam_number in range(2,-1,-1):
    ###    for cam_number in range(0,3):
    ###        print(('Try camera %d.' % cam_number))
    ###        cam = cv2.VideoCapture(cam_number)
    ###        if cam.isOpened():
    ###            break
    ###    if not cam.isOpened():
    ###        sys.stderr.write('ERROR: Did not connect to a camera.\n')
    ###        sys.exit(1)
    cam = cv2.VideoCapture(camera_number)
    if not cam.isOpened():
        raise RuntimeError("ERROR: Could not open camera %d." % (camera_number))

    print(("Running with camera number %d." % camera_number))
    print("Set next camera shot.")
    print(type(cam))
    print(str(cam))
    ## 320*240 = 76800 pixels
    # cam.set(3,320)
    # cam.set(4,240)
    ## 640*480 = 307200 pixels
    cam.set(3,640)
    cam.set(4,480)
    ## 640*480 = 230400 pixels (AR:16/9)
    #cam.set(3, 640)
    #cam.set(4, 480)
    ## 800*600 = 480000 pixels
    # cam.set(3,CAM_RES_X)
    # cam.set(4,CAM_RES_Y)
    ## 1024*768 = 786432 pixels
    # cam.set(3,1024)
    # cam.set(4,768)
    # 720P (AR:16/9)
    # 1280*720 = 921600
    #    cam.set(3,1280)
    #    cam.set(4,720)
    ## 1080P
    ## 1920*1080 = 2074800 pixels
    # cam.set(3,1920)
    # cam.set(4,1080)
    # cam.set(cv2.CAP_PROP_AUTOFOCUS, 0) # turn the autofocus off
    # cam.set(cv2.CAP_PROP_AUTOFOCUS, 1) # turn the autofocus on
    return cam

def handle_bug_raise_window_to_top ():
    # This is due to a stupid bug in OpenCV.
    # This technique is almost certain to break at some point.
    if os.access("/usr/bin/osascript", os.X_OK):
        if sys.version_info[0] == 3:
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python3" to true' ''')
        else:
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')


def main(argv):

    if len(argv) > 1:
        camera_number = int(argv[1])
    else:
        camera_number = 0
    cam = open_camera(camera_number)

    WindowName = "current view %d" % (camera_number)
    cv2.namedWindow(WindowName,cv2.WINDOW_NORMAL)
    cv2.moveWindow(WindowName,10,10)
    # These two lines will force window to be on top with focus.
    cv2.setWindowProperty(WinName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty(WinName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_NORMAL)

    CAMERA_DIR = "MOVEMENT-%d" % camera_number

    # Seed the queue.
    t_minus = cam.read()[1]
    t_now = cam.read()[1]
    t_minus = cv2.resize(t_minus, (640, 480))
    t_now = cv2.resize(t_now, (640, 480))
    t_now_raw = t_now.copy()
    t_plus_raw = t_plus.copy()
    delta_count_last = 1
    # HYSTERESIS =

    try:
        os.mkdir(CAMERA_DIR)
    except:
        print("Did not make dir: %s" % CAMERA_DIR)
        pass

    # The old date and time handler.
    #    now=time.time()
    #    # Copy fractions of a second from epoch because strftime does not support it.
    #    frac_seconds_str=("%.4f"%(math.modf(now)[0]))[1:]
    #    now_date = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(now)) + frac_seconds_str

    snapshot_interval = 600
    # start_time_epoch = datetime.now().timestamp()
    start_time_epoch = time.time()
    record_video_state = False
    last_epoch = start_time_epoch
    count = 0
    while True:
        now = datetime.now()
        now_date = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
        # now_epoch = now.timestamp()
        now_epoch = time.time()

#t_plus_raw = t_plus.copy()
        t_now_raw = t_now.copy()
#        t_plus = cv2.medianBlur(t_plus, 17)
#        delta_view = delta_images(t_minus, t_now, t_plus)
        #delta_view = motion_view(t_minus, t_now, t_plus)
        delta_view = cv2.absdiff(t_minus, t_now)
        #    cv2.morphologyEx(delta_view, cv2.MORPH_OPEN, kernel)
        #    cv2.morphologyEx(delta_view, cv2.MORPH_CLOSE, kernel)
        # new
        delta_view = cv2.GaussianBlur(delta_view,(5,5),0)
        # th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
        retval, delta_view = cv2.threshold(delta_view, 16, 255, 3)
        cv2.normalize(delta_view, delta_view, 0, 255, cv2.NORM_MINMAX)
#        cv2.imshow(WindowName, delta_view)
        img_count_view = cv2.cvtColor(delta_view, cv2.COLOR_RGB2GRAY)
        delta_count = cv2.countNonZero(img_count_view)
        delta_factor = delta_count / (img_count_view (640.0 * 480.0)
#        retval, img_count_view = cv2.threshold(img_count_view, 40,255,cv2.THRESH_BINARY)
#        raw_gray=cv2.cvtColor(t_plus_raw, cv2.COLOR_RGB2GRAY)
        b,g,r=cv2.split(t_now_raw)
        r = cv2.addWeighted(r,0.7,img_count_view,0.8,0)
        g = cv2.addWeighted(g,0.7,img_count_view,0.8,0)
        cv2.merge((b,g,r), t_now_raw)
        #    # mirror view
        # delta_view = cv2.flip(delta_view, 1)
        if (
            delta_count_last < DELTA_COUNT_THRESHOLD
            and delta_count >= DELTA_COUNT_THRESHOLD
        ):
            record_video_state = True
            # sys.stdout.write("MOVEMENT %f\n" % now.timestamp())
            sys.stdout.write("MOVEMENT %s\n" % str(now))
            sys.stdout.flush()
        elif (
            delta_count_last >= DELTA_COUNT_THRESHOLD
            and delta_count < DELTA_COUNT_THRESHOLD
        ):
            record_video_state = False
            # sys.stdout.write("STILL    %f\n" % now.timestamp())
            sys.stdout.write("STILL    %s\n" % str(now))
            sys.stdout.flush()
        output_filename_frame = "%s/frame.%s.jpg" % (CAMERA_DIR, now_date)
        output_filename_delta = "%s/delta.%s.jpg" % (CAMERA_DIR, now_date)
        #    output_filename_frame = 'MOVEMENT/f%13.2f.jpg' % (now)
        #    output_filename_delta = 'MOVEMENT/d%13.2f.jpg' % (now)
        #    output_filename_frame = 'MOVEMENT/f%13.4f-%s.jpg' % (now, now_date)
        #    output_filename_delta = 'MOVEMENT/d%13.4f-%s.jpg' % (now, now_date)
        # label_text="date: %s delta%%:%3d file: %s" % (now_date,int(delta_factor*100),output_filename_frame)
        label_text = "delta:%3d%% %s" % (int(delta_factor * 100), output_filename_frame)
        label_ul = (1, 18)
        label_text_ul = (2, 18)
        label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_PLAIN, 0.8, 1)[0]
        label_lr = (label_ul[0] + label_size[0] + 1, label_ul[1] - label_size[1] - 7)
        if record_video_state:
            cv2.rectangle(t_now_raw, label_ul, label_lr, (0, 0, 255), -1)
        else:
            cv2.rectangle(t_now_raw, label_ul, label_lr, (0, 0, 0), -1)
        cv2.putText(
            t_now_raw,
            label_text,
            label_text_ul,
            cv2.FONT_HERSHEY_PLAIN,
            0.8,
            (255, 255, 255),
        )
        #    cv2.putText(delta_view, label_text, label_text_ul, cv2.FONT_HERSHEY_PLAIN, 0.75, (255,255,255))
##        cv2.imshow(WindowName, delta_view)
#        cv2.imshow(WindowName, t_now_raw)
#        cv2.imshow(WindowName, t_plus)
#        cv2.imshow(WindowName, img_count_view)
        cv2.imshow(WindowName, t_now_raw)
        if record_video_state == True or (now_epoch - last_epoch > snapshot_interval):
            if now_epoch - last_epoch > snapshot_interval:
                sys.stdout.write("SNAPSHOT %f\n" % now_epoch)
                sys.stdout.flush()
            last_epoch = now_epoch
            cv2.imwrite(output_filename_frame, t_now_raw)
        #        cv2.imwrite(output_filename_frame, t_plus_raw)
        #        cv2.imwrite(output_filename_delta,delta_view)
        delta_count_last = delta_count
        # move images through the queue.
        t_minus = t_now
        t_now = t_plus
#        t_plus = cv2.blur(t_plus, (8, 8))
        # Get the new t_plus image.
        try:
            t_plus = cam.read()[1]
        except:
            # This is a lame way to deal with this exception.
            cam.release()
            time.sleep(0.9)
            cam = open_camera(camera_number)
            time.sleep(0.9)
            t_plus = cam.read()[1]
#        t_plus_raw = t_plus.copy()
        ##FIXME        t_plus = cv2.resize(t_plus, (640, 480))
#        t_plus = cv2.blur(t_plus, (8, 8))
###>        t_plus = cv2.medianBlur(t_plus, 17)
#        t_plus = cv2.bilateralFilter(t_plus, 8, 150,8) 
        # t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2BGR)
        # t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
        # t_plus = cv2.bilateralFilter(t_plus,9,75,75)

        # Wait up to 10ms for a key press.
        # If the key is the ESC or 'q' then quit.
        key = cv2.waitKey(10)
        if key == 0x1B or key == ord("q"):
            cv2.destroyWindow(WindowName)
            break


if __name__ == "__main__":
    main(sys.argv)

# vim: set ft=python fileencoding=utf-8 sr et ts=4 sw=4 : See help 'modeline'
