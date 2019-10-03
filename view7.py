#!/usr/bin/env python3

import cv2
import numpy
import os
import os.path
import sys


def show_status(dataset_index,dataset_size,percent,filename,disposition,step,play_speed,pause_flag):

    if disposition==0:
        disp_msg='pause at ends'
    elif disposition==1:
        disp_msg='loop around ends'
    elif disposition==2:
        disp_msg='reverse at ends'
    sys.stdout.write('\033[1;1H')  # CUP: Cursor Position to column 1, row 1.
    sys.stdout.write('\033[2K')  # EL: Erase in Line. 2 specifies the entire current line.
    if pause_flag:
        sys.stdout.write('%d/%d %d%% %s step:%d speed:PAUSED(%dms) disposition:%s'%(dataset_index,dataset_size,percent,filename,step,play_speed,disp_msg))
    else:
        sys.stdout.write('%d/%d %d%% %s step:%d speed:%dms disposition:%s'%(dataset_index,dataset_size,percent,filename,step,play_speed,disp_msg))
    sys.stdout.flush()

def show_help():

    sys.stdout.write('\033[2J')  # ED: Erase in Display. 2 specifies clear entire visible screen.
    sys.stdout.write('\033[1;1H')  # CUP: Cursor Position to column 1, row 1.
    sys.stdout.write('''
   ? : Show this help message in console.
   X : Hide frame from playback. Does not delete file.
 t/T : Turn frame 90 degrees clockwisei/counterclockwise.
   r : Reverse play direction.
   s : Slower play speed. Increase delay between frames in milliseconds.
   f : Faster play speed. Decrease delay between frames in milliseconds.
 SPACE Toggle between pause and the current play speed.
   < : Pause and single step frame backward.
   > : Pause and single step frame forward.
  <- : Left Arrow, skip backward by 1% of the frames in the list.
  -> : Right Arrow, skip forward by 1% of the frames in the list.
 0-9 : Skip index to tenth of the list multiplied by the given digit.
        0% 10% 20% 30% 40% 50% 60% 70% 80% 90%
   - : Skip index to the end (100%) of the list.
   p : Select disposition when index hits either end.
       0: Pause when ends are hit.
       1: Loop around to other end when ends are hit (Loop Cycle).
       2: Reverse payback when ends are hit (Patrol Cycle).

   ''')
    sys.stdout.flush()

def main (argv):
    if len(argv)>1:
        imageDir = argv[1]
    else:
        imageDir = "."

    image_path_list = [x for x in os.listdir(imageDir) if os.path.splitext(x)[1].lower() == '.jpg']
    if len(image_path_list) == 0:
        image_path_list = [x for x in os.listdir(imageDir) if os.path.splitext(x)[1].lower() == '.png']
    if len(image_path_list) == 0:
        raise Exception('Could not find any .jpg or .png files in the given directory.')

    image_path_list = sorted(image_path_list)

    WindowName="Main View"
    cv2.namedWindow(WindowName, cv2.WINDOW_NORMAL)
    cv2.moveWindow(WindowName,10,10)
    # These two lines will force window to be on top with focus.
    cv2.setWindowProperty(WindowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty(WindowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_NORMAL)

#    print("Number Images: %d" % (len(image_path_list)))
    show_help()
    image_path_deleted_list=[]
    play_speed=1
    pause_flag=True
    index=0
    step=1
    turn=0
    AT_ENDS_PAUSE=0
    AT_ENDS_LOOP=1
    AT_ENDS_REVERSE=2
    disposition=AT_ENDS_PAUSE
    while len(image_path_list)>0:
        filename=image_path_list[index]
        percent=int(index/(len(image_path_list)-1)*100)
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

        show_status(index,len(image_path_list)-1,percent,filename,disposition,step,play_speed,pause_flag)
        label_text = "delta:%3d%% %s" % (int(delta_factor * 100), output_filename_frame)
        label_ul = (5, 15)
        label_text_ul = (7, 15)
        label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_PLAIN, 1.0, 1)[0]
        label_lr = (label_ul[0] + label_size[0] + 2, label_ul[1] - label_size[1] - 2)
        cv2.rectangle(img, label_ul, label_lr, (0, 255, 255), -1)
        cv2.putText(
            img,
            label_text,
            label_text_ul,
            cv2.FONT_HERSHEY_PLAIN,
            1.0,
            (255, 255, 255),
        )
        #    cv2.putText(delta_view, label_text, label_text_ul, cv2.FONT_HERSHEY_PLAIN, 0.75, (255,255,255))
        cv2.imshow(WindowName, img)
        if pause_flag:
            key=cv2.waitKey(0)
        else:
            key=cv2.waitKey(play_speed)

        if key == 27 or key == ord('q'):
            # QUIT, EXIT, END, DONE, STOP, BREAK, TERMINATE, HALT.
            break
        if key == ord('?'):
            # Help.
            show_help()
            pause_flag=True
            continue
        if key == ord(' '):
            # Pause or unpause playback.
            pause_flag=not pause_flag
            continue
        if key == ord('X'):
            # Hide image from playback.
            image_path_deleted_list.append(image_path_list[index])
            del(image_path_list[index])
            if index >= len(image_path_list):
                index = len(image_path_list)-1
            if index < 0:
                print("Deleted last image. Nothing left to do.")
                break
            continue
        if key == ord('t'):
            # Turn playback clockwise.
            turn=turn+1
            if turn>3:
                turn=0
            continue
        if key == ord('T'):
            # Turn playback counterclockwise.
            turn=turn-1
            if turn<0:
                turn=3
            continue
        elif key == ord('r'):
            # reverse playback step direction.
            step=step * -1
            continue
        elif key == ord('s'):
            # slower
            # 1 2 4 8 16 32 64 128 256 512 1024 2048
            if play_speed < 4096:
                play_speed=int(play_speed*2)
            continue
        elif key == ord('f'):
            # faster
            if play_speed >= 2:
                play_speed=int(play_speed/2)
            continue
        elif key == ord('p'):
            # Select disposition when playback hits either end.
            # AT_ENDS_PAUSE(0) will pause at either end.
            # AT_ENDS_LOOP(1) will loop to other end when either end is hit.
            # AT_ENDS_REVERSE(2) will reverse playback direction when either end is hit.
            disposition=disposition+1
            if disposition>AT_ENDS_REVERSE:
                disposition=AT_ENDS_PAUSE
            continue

        # Handle updates to the current index of the frame to be displayed.
        # This includes manually skipping the index around the image list, and
        # the typical playback by moving the index based on the step.
        if key >= ord('0') and key <= ord('9'):
            # Manually skip to a tenth fraction of image list.
            point=key-ord('0')
            point=point/10.0
            highest_index=len(image_path_list)
            index=int(highest_index * point)
        elif key == ord('-') or key == ord('_'):
            # Manually skip to end of image list.
            index=len(image_path_list)-1
        elif key == ord(',') or key == ord('<'):
            # Single step backward. Start by pausing playback.
            if not pause_flag:
                pause_flag=True
                continue
            index=index-abs(step)
        elif key == ord('.') or key == ord('>'):
            # Single step forward. Start by pausing playback.
            if not pause_flag:
                pause_flag=True
                continue
            index=index+abs(step)
        elif key == 2:  # Left cursor arrow <-.
            # Skip index backward 1% in image list. Start by pausing playback.
            if not pause_flag:
                pause_flag=True
                continue
            one_percent=int(numpy.ceil(len(image_path_list)/100))
            index=index-one_percent
        elif key == 3:  # Right cursor arrow ->.
            # Skip index forward 1% in image list. Start by pausing playback.
            if not pause_flag:
                pause_flag=True
                continue
            one_percent=int(numpy.ceil(len(image_path_list)/100))
            index=index+one_percent
        elif key == -1:  # No key was pressed. Normal playback.
            index=index+step
        else:  # Some unhandled key was pressed. Ignore it.
            sys.stdout.write ('Key value:  %d' %(key) )
            continue

        # Handle index moving past the ends of the list.
        # The disposition variable tells how to handle the ends.
        if index<0:
            if disposition==AT_ENDS_PAUSE:
                index=0
                pause_flag=True
            elif disposition==AT_ENDS_LOOP:
                index=len(image_path_list) - 1
            elif disposition==AT_ENDS_REVERSE:
                index=0
                step=step * -1
        elif index>=len(image_path_list):
            if disposition==AT_ENDS_PAUSE:
                index=len(image_path_list) - 1
                pause_flag=True
            elif disposition==AT_ENDS_LOOP:
                index=0
            elif disposition==AT_ENDS_REVERSE:
                index=len(image_path_list) - 1
                step=step * -1

    # Outside of main loop. The program terminates after this.
    cv2.destroyAllWindows()
    sys.stdout.write('\033[2J')  # ED: Erase in Display. 2 specifies clear entire visible screen.
    sys.stdout.write('\n')
    sys.stdout.flush()
    # If any frames were hidden then print a report of those for the user.
    if len(image_path_deleted_list) > 0:
        image_path_deleted_list.sort()
        print()
        print('The following names were deleted from the main index.')
        print('The original files were not modified, moved, or deleted.')
        print('If you wish to delted these files then you must do so manually.')
        for filename in image_path_deleted_list:
            print(filename)

if __name__ == '__main__':
    main(sys.argv)
