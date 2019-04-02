#!/usr/bin/env python3

'''
SYNOPSIS

    serve_jpeg.py

DESCRIPTION

    This is a CGI script that will serve a directory fille of JPEG imaages as the MJPEG steram (motion JPEG).
    You do need to modiy the "image_file_dir" variable to set the directory where jpeg files will be served from.
    For example:
        image_file_dir = "/home/noah/public/video_frames"
    You may also adjust the max_FPS value to adjust the playback speed. For example, to set 10 FPS:
        max_FPS = 10
    The playback server will not skip frames, so the actual playback speed may me slower than your
    max_FPS if the connection speed is slow.
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

    Version 1
'''

__version__ = 'Version 1'
__date__ = ''
__author__ = 'Noah Spurrier <noah@noah.org>'

#import cv2
import time
import os
import glob
import sys
import logging
import cgi
import urllib

def render_main_page (submit_src, image_file_dir, max_FPS, start_at, start_at_index, start_at_time_quote_plus, start_at_time):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="ie=edge">
<title>MJPEG Player</title>

<style type="text/css">
body
{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10pt;
    color: #000000;
    background-color: #ffffff;
}
a
{
    color: #0000ff; text-decoration: none
}
a:hover
{
    color: #ff0000
}
</style>
</head>
<body>

<form action="http://www.noah.org/cgi-bin/mjpeg_player.py" action="GET">
<table style="border: 1px solid black">
<caption>MJPEG Player</caption>
<tbody>
<tr>
    <td colspan="10" style="background: black"><img src="%(submit_src)s?stream=1&image_file_dir=%(image_file_dir)s&max_FPS=%(max_FPS)d&start_at=%(start_at)d&start_at_index=%(start_at_index)d&start_at_time=%(start_at_time_quote_plus)s" alt="MJPEG container" id="mjpeg_container" width="640" height="360"></td>
</tr>
<tr>
    <td><input type="submit" name="start_at" value="0"></td>
    <td><input type="submit" name="start_at" value="10"></td>
    <td><input type="submit" name="start_at" value="20"></td>
    <td><input type="submit" name="start_at" value="30"></td>
    <td><input type="submit" name="start_at" value="40"></td>
    <td><input type="submit" name="start_at" value="50"></td>
    <td><input type="submit" name="start_at" value="60"></td>
    <td><input type="submit" name="start_at" value="70"></td>
    <td><input type="submit" name="start_at" value="80"></td>
    <td><input type="submit" name="start_at" value="90"></td>
</tr>
<tr>
    <td colspan="8"><input type="submit" name="play" value="Load Directory"><input type="text" size="60" name="image_file_dir" value="%(image_file_dir)s"></td>
    <td><input type="submit" name="max_FPS_submit" value="FPS"><input type="text" size="4" name="max_FPS" value="%(max_FPS)d"></td>
</tr>
<tr>
    <td colspan="5"><input type="submit" name="start_at_index_submit" value="Start at Index"><input type="text" size="10" name="start_at_index" value="%(start_at_index)d"></td>
    <td colspan="5"><input type="submit" name="start_at_time_submit" value="Start at Time"><input type="text" size="20" name="start_at_time" value="%(start_at_time)s"></td>
</tr>
</tbody>
</table>
</form>
</body>
</html>
""" % locals()

if __name__ == "__main__":

# rc,img = capture.read()
# image_file_contents=cv2.imencode('.jpg', img)[1].tostring()

    logging.basicConfig(level=logging.DEBUG, filename='mjpeg_player.py.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#    sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)

    form = cgi.FieldStorage()
    try:
        start_at_index = int(form.getvalue('start_at_index','-1'))
    except:
        start_at_index = -1
    try:
        start_at_time = str(form.getvalue('start_at_time','1700-01-01 15:42'))
    except:
        start_at_time = '1700-01-01 15:42'
    try:
        stream = int(form.getvalue('stream',0))
    except:
        stream = 0
    try:
        max_FPS = int(form.getvalue('max_FPS',30))
    except:
        max_FPS = 30
    try:
        start_at = int(form.getvalue('start_at','0'))
    except:
        start_at = 0
    try:
        image_file_dir = str(form.getvalue('image_file_dir', '/home/noahspurrier/noah.org/public/SEER-0'))
    except:
        image_file_dir = '/home/noahspurrier/noah.org/public/SEER-0'

    if not stream:
        sys.stdout.buffer.write (b'Content-Type: text/html\r\n')
        sys.stdout.buffer.write (b'\r\n')
        sys.stdout.flush()
        submit_src="http://www.noah.org/cgi-bin/mjpeg_player.py"
#        submit_src= f"{base_URL}?stream=1&image_file_dir={image_file_dir}&start_at={start_at}&max_FPS={max_FPS}"
        page_string = render_main_page(submit_src, image_file_dir, max_FPS, start_at, start_at_index, urllib.parse.quote_plus(start_at_time),start_at_time)
        sys.stdout.buffer.write(page_string.encode())
        sys.exit(0)

    # Stream the video directory.
    # Some sources say to include '--' in the boundry definition in the Content-Type header.
    # Other sources say not to include this. Both seem to work. It seems more correct to not include here.
    sys.stdout.buffer.write (b'Content-Type: multipart/x-mixed-replace; boundary="jpegboundary"\r\n')
    sys.stdout.buffer.write (b'Connection: close\r\n')
    sys.stdout.buffer.write (b'Max-Age: 0\r\n')
    sys.stdout.buffer.write (b'Expires: 0\r\n')
    sys.stdout.buffer.write (b'Cache-Control: no-cache, private\r\n')
    sys.stdout.buffer.write (b'Pragma: no-cache\r\n')
    sys.stdout.buffer.write (b'\r\n')
    sys.stdout.flush()
    image_file_list = glob.glob(os.path.join(image_file_dir,'*.jpg'))
    image_file_list.sort()

    if max_FPS<=0:
        max_FPS=1000000
    delay_per_frame=1.0/max_FPS
    start_index=int(float(len(image_file_list))*(start_at/100.0))
    for image_filename in image_file_list[start_index:]:
        frame_start_time = time.time()
        try:
            fin=open(os.path.join(image_file_dir, image_filename),'rb')
            image_file_contents=fin.read()
            fin.close()
        except:
            continue
        try:
            sys.stdout.buffer.write (b'--jpegboundary\r\n')
            sys.stdout.buffer.write (b'Content-type: image/jpeg\r\n')
            cls = 'Content-length: %s\r\n' % str(len(image_file_contents))
            sys.stdout.buffer.write (cls.encode())
            sys.stdout.buffer.write (b'\r\n')
            sys.stdout.buffer.write (image_file_contents)
            sys.stdout.buffer.write (b'\r\n')
            sys.stdout.flush()
        except Exception as inst:
            logging.info(type(inst))
            logging.info(inst.args)
            logging.info(inst)
            break
        delay = delay_per_frame-(time.time()-frame_start_time)
        if delay>0:
            time.sleep(delay)
    sys.stdout.buffer.write (b'--jpegboundary--\r\n')
    sys.stdout.flush()

