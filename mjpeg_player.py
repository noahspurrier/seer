#!/usr/bin/env python3

'''
SYNOPSIS

    mjpeg_player.py

DESCRIPTION

    This will taken an entire directory of jpeg images and play them back as a
    video. Each jpeg is a separate frame in the video. You can play forwards
    and backwards at different rates of speed. You can stop and single step in
    either direction. You can remove individial frames from the video playback.
    The file remains in the directory, but once you quit the viewer you will be
    shown a list of filenames that were removed from the playback. You may then
    deal with these files as you like. All UI control is via the keyboad, so
    manipulaation of playback is fast. The plan is to turn this into a simple,
    primitive video editor.

AUTHOR

    Noah Spurrier <noah@noah.org>

LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2019, Noah Spurrier <noah@noah.org>
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

    Version 1
'''

__version__ = 'Version 1'
__date__ = '2019-03-31'
__author__ = 'Noah Spurrier <noah@noah.org>'

import cv2
import numpy
import os, os.path
import sys

def main (argv):
    if len(argv)>1:
        imageDir = argv[1]
    else:
        imageDir = "."

    image_path_list = [x for x in os.listdir(imageDir) if os.path.splitext(x)[1] == '.jpg']
    image_path_list = sorted(image_path_list)

    WindowName="Main View"
    cv2.namedWindow(WindowName, cv2.WINDOW_NORMAL)
    cv2.moveWindow(WindowName,10,10)
    # These two lines will force window to be on top with focus.
    cv2.setWindowProperty(WindowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty(WindowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_NORMAL)

    print("Number Images: %d" % (len(image_path_list)))
    print("""   X : Delete frame from list (does not delete file).
   b : Set the soft beginning of the video.
   B : Reset the soft beginning of the video.
   e : Set the soft ending of the video.
   E : Reset the soft ending of the video.
   t : Turn frame 90 degrees clockwise. Keep hitting to keep turning.
   r : Reverse direction.
   s : Slower. Keep hitting to play even slower.
   f : Faster. Keep hitting to play even faster.
   p : Select disposition for index past ends of the frame list.
       0: Stop at ends.
       1: Loop around from one end to the other.
       2: Bounce off ends and reverse direction.
 SPACE Toggle pause. When unpausing return to prevous speed.
   < : Pause and single step backward.
   > : Pause and single step forwrds.
  <- : Left Arrow, skip backwards by 1% of the frames in the list.
  -> : Right Arrow, skip forwards by 1% of the frames in the list.
 0-9 : Skip index to tenth of the list multiplied by the given digit.
        0% 10% 20% 30% 40% 50% 60% 70% 80% 90%
   - : Skip index to the end (100%) of the list.
   """)

    print("Paused. Press space to unpause.")
    image_path_deleted_list=[]
    wait_key_delay_speed_rolling = 1
    wait_key_delay = 0
    index=0
    step=1
    STOP=0
    LOOP=1
    BOUNCE=2
    turn=0
    disposition=STOP
    soft_beginning=0
    soft_ending=len(image_path_list)
    while len(image_path_list)>0:
        filename=image_path_list[index]
        percent=int(index/(len(image_path_list)-1)*100)
        print("%d/%d %d%% %s disp:%d step:%d speed:%d"%(index,(len(image_path_list)-1),percent,filename,disposition,step,wait_key_delay))
        img = cv2.imread(os.path.join(imageDir, filename))
        if img is None:
            print("No image for: %s"%(filename))
        else:
            if turn == 1:
                img=cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            elif turn == 2:
                img=cv2.rotate(img, cv2.ROTATE_180)
            elif turn == 3:
                img=cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            cv2.imshow(WindowName,img)

        key = cv2.waitKey(wait_key_delay)


        if key == ord('X'):
            image_path_deleted_list.append(image_path_list[index])
            del(image_path_list[index])
            if index >= len(image_path_list):
                index = len(image_path_list)-1
            if index < 0:
                print("Deleted last image. Nothing left to do.")
                break
            continue
        elif key == ord('B'):
            soft_beginning = 0
        elif key == ord('b'):
            soft_beginning = index
            continue
        elif key == ord('E'):
            soft_ending = len(image_path_list)
        elif key == ord('e'):
            soft_ending  = index
            continue
        elif key == ord('t'):
            # FIXME Make this an enum, please.
            turn = turn + 1
            if turn > 3:
                turn = 0
            continue
        elif key >= ord('0') and key <= ord('9'):
            point=key-ord('0')
            point=point/10.0
            soft_length=soft_ending-soft_beginning
            index=soft_beginning + int(soft_length * point)
            continue
        elif key == ord('-') or key == ord('_'):
            index=soft_ending - 1
            continue
        elif key == ord(' '):
            if wait_key_delay == 0:
                wait_key_delay = wait_key_delay_speed_rolling
            else:
                wait_key_delay = 0
            continue
        elif key == ord('r'):
            # reverse direction.
            step=step * -1
        elif key == ord('s'):
            # slower
            # 1 2 4 8 16 32 64 128 256 512 1024 2048
            if wait_key_delay_speed_rolling < 4096:
                wait_key_delay_speed_rolling=int(wait_key_delay_speed_rolling*2)
            wait_key_delay = wait_key_delay_speed_rolling
        elif key == ord('f'):
            # faster 
            if wait_key_delay_speed_rolling >= 2:
                wait_key_delay_speed_rolling=int(wait_key_delay_speed_rolling/2)
            wait_key_delay = wait_key_delay_speed_rolling
        elif key == ord('p'):
            # change disposition when hitting end.
            # STOP(0) will freeze at either end.
            # LOOP(1) will loop to other end when end is hit.
            # BOUNCE(2) will reverse direction when end is hit.
            disposition=disposition+1
            if disposition>BOUNCE:
                disposition=STOP
        elif key == ord('.'):
            # single step forwards.
            # single step also triggers pause.
            wait_key_delay=0
            index=index+abs(step)
        elif key == ord(','):
            # single step backwards.
            # single step also triggers pause.
            wait_key_delay=0
            index=index-abs(step)
        elif key == 2: # Left cursor arrow.
            one_percent=int((soft_ending-soft_beginning)/100)
            index=index-one_percent
        elif key == 3: # Right cursor arrow.
            one_percent=int((soft_ending-soft_beginning)/100)
            index=index+one_percent
        elif key == 27 or key == ord('q'):
            break
        else:
            index = index + step

        # Handle index moving past the ends of the list.
        if index < soft_beginning:
            if disposition==STOP:
                index=soft_beginning
                wait_key_delay = 0
            elif disposition==LOOP:
                index=soft_ending - 1
            elif disposition==BOUNCE:
                index=soft_beginning
                step=step * (-1)
        elif index >= soft_ending:
            if disposition==STOP:
                index=soft_ending - 1
                wait_key_delay = 0
            elif disposition==LOOP:
                index=soft_beginning
            elif disposition==BOUNCE:
                index=soft_ending - 1
                step=step * (-1)

    cv2.destroyAllWindows()

    if len(image_path_deleted_list) > 0:
        image_path_deleted_list.sort()
        print()
        print("The following names were deleted from the main index.")
        print("You may wish to delete the files manually.")
        for filename in image_path_deleted_list:
            print(filename)

if __name__ == '__main__':
    main(sys.argv)
