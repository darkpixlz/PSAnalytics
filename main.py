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


@app.route('/error-logs', methods=['POST'])
def error_logs():
    error_data = json.loads(request.data.decode('utf-8'))
    error_contents = error_data.get('ErrorContents', '')
    place_id = error_data.get('PlaceId', '')
    log_entry = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} / {place_id}]: {error_contents}\n"

    with open('files/error_logs.txt', 'a') as f:
        f.write(log_entry)

    return 'Logged error successfully.'

@app.route('/asset-loaded', methods=['POST'])
def assets_loaded():
    data = json.loads(request.data)
    assets_loaded = data['AssetsLoaded']
    place_id = str(data['PlaceId'])
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open('files/AssetsLoaded.json', 'r+') as f:
        try:
            file_data = json.load(f)
        except json.JSONDecodeError:
            file_data = {}

        # Check if the place_id already exists in the data
        if place_id in file_data:
            # Update the existing entry with the new assets_loaded value
            file_data[place_id]['AssetsLoaded'] += assets_loaded
        else:
            # Create a new entry for the place_id
            file_data[place_id] = {'AssetsLoaded': assets_loaded, 'PlaceId': place_id}

        # Check if it's a new day
        if not file_data or datetime.datetime.strptime(list(file_data.keys())[-1], '%Y-%m-%d %H:%M:%S').date() != datetime.datetime.now().date():
            # If it's a new day, add a new entry to the file
            file_data[timestamp] = {place_id: file_data[place_id]}
        else:
            # If it's the same day, update the last entry in the file
            last_key = list(file_data.keys())[-1]
            file_data[last_key][place_id] = {**file_data[last_key][place_id], 'AssetsLoaded': file_data[place_id]['AssetsLoaded']}

        # Write the updated data back to the file
        f.seek(0)
        json.dump(file_data, f, indent=2)

    return 'Assets loaded successfully.'



def Rotate():
    todays_servers = len(placeids)
    analytics = [obj for obj in json.loads(
        open("files/analytics.json", "r").read())]
    analytics.append(
        f"{[datetime.datetime.now().split(' ')[0]]} = {todays_servers}")
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


CorrectKey = ""


@app.route("/analytics/download/<PrivateKey>", methods=["GET"])
def download(PrivateKey):
    if CorrectKey == PrivateKey:
        return open("analytics.json").read()
    else:
        abort(401)


app.run(
    port=80,
    host="0.0.0.0"
)
