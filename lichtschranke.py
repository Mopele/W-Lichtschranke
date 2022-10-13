# Importing Libraries
# creating executable:
##      python -m PyInstaller --onefile .\lichtschranke.py
import ctypes
import serial
from serial.tools import list_ports
import sys
from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, send, emit
from multiprocessing import Process, Value
import logging

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app)
video_trigger = Value(ctypes.c_bool, False)
sensor_lock = Value(ctypes.c_bool, True)

class AjaxFilter1(logging.Filter):
    def filter(self, record):  
        return "socket.io" not in record.getMessage()
class AjaxFilter2(logging.Filter):
    def filter(self, record):  
        return "static" not in record.getMessage()

log = logging.getLogger('werkzeug')
log.addFilter(AjaxFilter1())
log.addFilter(AjaxFilter2())

def portscan():
    for i in list_ports.comports():
        print(f"Port {i} found")
    return
def autoconnect():
    for i in list_ports.comports():
        try:
            arduino = serial.Serial(port=f"{i.device}", baudrate=115200, timeout=.1)
            print(f"Arduino connected on port {i.device}")
            return arduino
        except Exception as e:  
            print(f"Arduino not connected on port {i.device}: {str(e)}")
@app.route('/toggle_sensor') 
def toggle_sensor(): 
    sensor_lock.value = not sensor_lock.value
    return redirect(url_for('control'))

def listener(video_trigger, sensor_lock, com_port):
    try:
        if (com_port == None): arduino = autoconnect()
        else: arduino = serial.Serial(port=com_port, baudrate=115200, timeout=.1)
    except Exception as e:  
        print(f"Arduino not connected on port {com_port}: {str(e)}")
        sys.exit()
    while True:
        if(arduino.readline().decode("utf-8").replace("\n", "").replace("\r", "") == "Trigger"):
            print("Trigger")
            if sensor_lock.value: video_trigger.value = True

@app.route('/')
def index():
    return render_template('index.html')     

@app.route('/test')
def test():
    return render_template('test.html') 

@app.route('/control')
def control():
    if sensor_lock.value: return render_template('control.html', sensor_state="Unlocked")
    else: return render_template('control.html', sensor_state="Locked")

@socketio.on('request trigger')
def handle_request(data):
    if video_trigger.value:
        emit("trigger")
        video_trigger.value = False

if __name__ == "__main__":
    for arg in sys.argv:
        if arg.startswith("COM"): com_port = sys.argv[sys.argv.index(arg)]
        else: com_port = None
        if arg == "portscan":
            portscan()
            sys.exit()
        if arg == "help":
            print("Usage: python3 lichtschranke.py [COMx] [portscan] [help]")
            print("     COMx: COM port of Arduino")
            print("     portscan: Scans for available COM ports")
            print("     help: Shows this help")
            print("")
            print("Example: python3 lichtschranke.py COM3")
            print("")
            print("Drivers needed: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers")
            sys.exit()

    p = Process(target=listener, args=(video_trigger, sensor_lock, com_port))
    p.start()
    try:
        socketio.run(app, host='localhost', port=3000)
    except:
        sys.exit()
    p.join()


