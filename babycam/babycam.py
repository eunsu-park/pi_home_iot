import cv2
from flask import Flask, render_template, Response
from picamera2 import Picamera2, Preview

app = Flask(__name__)
camera = Picamera2()

camera.configure(camera.create_preview_configuration(main={"size": (640, 480)}))
camera.start()

def gen_frames():
    while True:
        frame = camera.capture_array()
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_brightness/<int:brightness>')
def set_brightness(brightness):
    camera.set_controls({"Brightness": brightness})
    return f"Brightness set to {brightness}"

@app.route('/set_contrast/<int:contrast>')
def set_contrast(contrast):
    camera.set_controls({"Contrast": contrast})
    return f"Contrast set to {contrast}"

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--address", type=str, help="Address to listen on")
    parser.add_argument("--port", type=int, help="Port to listen on")
    args = parser.parse_args()

    app.run(host=args.address, port=args.port)