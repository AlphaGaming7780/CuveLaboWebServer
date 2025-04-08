import threading
import time
import json
import random
from flask import Flask, Response, jsonify, request
from Common.LaboBase import LaboBase

class WebServerBase(object) :

    _labo : LaboBase
    _app : Flask
    _waterLevels : list[float]

    def __init__(self, labo : LaboBase):
        self._labo = labo
        self._app = Flask(__name__, static_url_path='')
        self._waterLevels = [0.0, 0.0, 0.0]

    @property
    def app(self) -> Flask:
        return self._app

    @app.route('/')
    def home(self):
        return self._app.send_static_file('index.html')

    @app.route('/event', methods=["GET"])  
    def event(self):
        # @stream_with_context
        def generate():
                while True:

                    obj = {
                        'time': time.strftime("%H:%M:%S", time.localtime()), # Pas vraiment bon, il peut dcp y avoir un décalage
                        'WaterLevel': self._waterLevels, 
                        'MotorSpeed': self._labo.GetMotorSpeed()
                    }

                    v = json.dumps(obj)

                    yield f"data:{v}\n\n"
                
                    time.sleep(1)

        return Response( generate(), mimetype='text/event-stream', content_type='text/event-stream', headers={ "Cache-Control": "no-cache", "Connection": "keep-alive" })

    @app.route('/GetWaterLevel', methods=["GET"])
    def GetWaterLevel(self):
        rep = jsonify(self._waterLevels)
        rep.status_code = 200
        return rep

    @app.route('/GetMotorSpeed', methods=["GET"])
    def GetMotorSpeed(self):
        rep = jsonify( self._labo.GetMotorSpeed() )
        rep.status_code = 200
        return rep

    @app.route('/SetMotorsSpeed', methods=["POST"])
    def SetMotorsSpeed(self):

        obj = {"idx": -1.0, "speed": -1.0}
        obj = request.json

        canRunMotor = self._labo.CanMotorRun(self._waterLevels)

        if(canRunMotor):
            self._labo.SetMotorSpeed(obj["idx"], obj["speed"])
        
        return Response(status=200)

    def Run(self):
        webServerThread = threading.Thread(target=lambda: self._app.run(host='0.0.0.0', debug=True, use_reloader=False))
        webServerThread.start()

        while(webServerThread.is_alive()):

            _waterLevels = self._labo.GetWaterLevels()
            print(f"Final value: {_waterLevels[0]}")

            if( not self._labo.CanMotorRun(_waterLevels) ) :
                self._labo.StopAllMotors()

            pass