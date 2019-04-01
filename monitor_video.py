#!/usr/bin/env python3

'''
SYNOPSIS

    monitor_video.py [-h,--help] [-v,--verbose] [--version]

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

    Version 4
'''

__version__ = 'Version 4'
__date__ = '2019-03-01 15:46:55:z'
__author__ = 'Noah Spurrier <noah@noah.org>'

import sys
import os
import traceback
import optparse
import time
import logging
import cv2
import numpy
import sys
import time
import datetime


def main(argv):
    camera_width = 640
    camera_height = 480

    if len(argv) > 1:
        camera_number = int(argv[1])
    else:
        camera_number = 0
    cam = cv2.VideoCapture(camera_number)
    if not cam.isOpened():
        raise RuntimeError("ERROR: Could not open camera %d." % (camera_number))
    cam.set(cv2.CAP_PROP_FRAME_WIDTH ,camera_width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT,camera_height)
    WindowName = "Monitor Camera: %d" % (camera_number)
    cv2.namedWindow(WindowName,cv2.WINDOW_NORMAL)
    if camera_number%4 == 0:
        cv2.moveWindow(WindowName,0,0)
    elif camera_number%4 == 1:
        cv2.moveWindow(WindowName,camera_width+5,0)
    elif camera_number%4 == 2:
        cv2.moveWindow(WindowName,0,camera_height+10)
    elif camera_number%4 == 3:
        cv2.moveWindow(WindowName,camera_width+5,camera_height+10)

    CAMERA_DIR = "MONITOR" # % camera_number

    # These two lines will force window to be on top with focus.
    cv2.setWindowProperty(WindowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty(WindowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_NORMAL)

#    # This is due to a stupid bug in OpenCV
#    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python3" to true' ''')

    try:
        os.mkdir(CAMERA_DIR)
    except:
        pass

    while True:

        video_now = cam.read()[1]
        now = datetime.datetime.now()
        now_date = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
        # now_epoch = now.timestamp()
        now_epoch = time.time()

        label_text = "%d: %s"%(camera_number, now_date)
        label_ul = (0, 11)
        label_text_ul = (2, 10)
        label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_PLAIN, 1.0, 1)[0]
        label_lr = (label_ul[0] + int(label_size[0]*0.8) + 2, label_ul[1] - label_size[1] - 1)
        cv2.rectangle(video_now, label_ul, label_lr, (0, 0, 0), -1)
        cv2.putText(
            video_now,
            label_text,
            label_text_ul,
            cv2.FONT_HERSHEY_PLAIN,
            0.8,
            (255, 255, 255),
        )

        cv2.imshow(WindowName, video_now)

        key = cv2.waitKey(10)
        # If the key is 's' or SPACE then save a frame.
        if key == ord('s') or key == ord(' '):
            print('Save frame.')
            output_filename_frame = "%s/frame.%d.%s.jpg" % (CAMERA_DIR, camera_number, now_date)
            cv2.imwrite(output_filename_frame, video_now)
        # If the key is the ESC or 'q' then quit.
        if key == 0x1b or key == ord('q'):
            cv2.destroyWindow(WindowName)
            break
        # If key is between '0' and '9' then connect to corresponding camera number.
        if key >= ord('0') and key <= ord('9'):
            cv2.destroyWindow(WindowName)
            camera_number = key-ord('0')
            cam = cv2.VideoCapture(camera_number)
            if not cam.isOpened():
                raise RuntimeError("ERROR: Could not open camera %d." % (camera_number))
            cam.set(3,camera_width)
            cam.set(4,camera_height)
            time.sleep(0.5)
            video_now = cam.read()[1]
            WindowName = "Monitor Camera: %d" % (camera_number)
            cv2.namedWindow(WindowName)
            cv2.moveWindow(WindowName,0,0)
            cv2.imshow(WindowName,video_now)

if __name__ == "__main__":
    main(sys.argv)

# vim: set ft=python fileencoding=utf-8 sr et ts=4 sw=4 : See help 'modeline'
