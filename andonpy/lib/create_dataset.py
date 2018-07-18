from flask import Flask, jsonify, render_template, request, Response, redirect, url_for
import logging as logging

from picamera import PiCamera
from picamera.array import PiRGBArray

import sys as sys
import os as os
import cv2 as cv

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

from .utility import Utility
util = Utility()

face_cascade = cv.CascadeClassifier(util.HAARPath())

class CreateDataset():

    def __init__(self):
        pass

@app.route('/')
def index():
    return render_template('create.html')


def createDataset(user):
    check_user = util.haveUser("books")
    if check_user[0] is "0":
        break

    with PiCamera(resolution=(1280, 720), framerate=40) as camera:
        print("[Initial] Camera is active...")
        print("[Initial] Please look at the camera and wait a minute...")

        camera.rotation = 180
        camera.brightness = 60
        camera.contrast = -5
        stream = PiRGBArray(camera)

        count = 0

        for frame in camera.capture_continuous(stream, format="bgr", use_video_port=True):
            if count == 15:
                print("[Successful] create 100 images")
                break
                # return redirect(url_for('shutdown'))

            image = frame.array
            gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                count += 1
                cv.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
                filename = check_user[0] + '.' + check_user[1] + "." + str(count) + ".jpg"
                cv.imwrite(os.path.join(check_user[2], filename), image[y:y+h, x:x+w])

            cv.imwrite("img.jpg", image)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + open('img.jpg', 'rb').read() + b'\r\n')

            stream.truncate()
            stream.seek(0)


@app.route('/frame')
def frame():
    return Response(createDataset(), mimetype='multipart/x-mixed-replace; boundary=frame')


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
