from flask import Flask, abort, render_template, request
import json
import datetime
import threading

app = Flask("PS_Analytics")
placeids = []

@app.route("/somethingelse/<ServerID>", methods=["POST"])
def Server(ServerID):
    try:
        print(f"ServerID is {ServerID}")
        postdata = request.get_json()
        placeids.append(postdata["PlaceID"])
        return "OK"
    except:
        return abort(400)

def Rotate():
    todays_servers = len(placeids)
    analytics = [obj for obj in json.loads(open("files/analytics.json", "r").read())]
    analytics.append(f"{[datetime.datetime.now().split(' ')[0]]} = {todays_servers}")
    with open("analytics.json", "a") as handle:
        handle.write(json.dumps(analytics))
    
def RotateScheduler():
    while True:
        CurrentTime = datetime.datetime.now().time()
        scheduled_time = datetime.time(hour=00, minute=00)
        if CurrentTime.hour == scheduled_time.hour and CurrentTime.minute == scheduled_time.minute:
            thread = threading.Thread(target=Rotate)
            thread.start()
            print("Rotating")
            thread.join()

app.run(
    port=80,
    host="0.0.0.0"
)