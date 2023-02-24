
from flask import Flask, abort, render_template, request
import json
import datetime
import threading
import csv

app = Flask("PS_Analytics")
placeids = []


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
    try:
        data = json.loads(request.data)
        assets_loaded = int(data['AssetsLoaded'])
        place_id = str(data['PlaceId'])
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except:
        abort(400)

    with open('Files/AssetsLoaded.csv', 'r') as file:
        NewFile = False
        if not file.read():
            NewFile = True
        NewAssetCount = False
        reader = csv.DictReader(file)
        rows = []
        RowToReplace = None  # initialize to None
        NewEntry = True
        for row in reader:
            if row[1] == place_id and row[0].split(" ")[0] == timestamp.split(" ")[0]:
                NewAssetCount = int(row["AssetsLoaded"]) + assets_loaded
                NewEntry = False
                rows.append(row)
                RowToReplace = row
            else:
                rows.append(row)
            if not NewAssetCount:
                NewEntry = True

        if not NewEntry and RowToReplace is not None:  # check if RowToReplace has been updated
            rows.remove(RowToReplace)
            rows.append([RowToReplace[0], RowToReplace[1], int(RowToReplace[2]) + assets_loaded])
        NewRows = rows

    with open('Files/AssetsLoaded.csv', 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Timestamp', 'PlaceID', 'AssetsLoaded'])
        if NewFile:
            writer.writeheader()

        if not NewEntry:
            writer.writerows(NewRows)

        if NewEntry:
            writer.writerow({'Timestamp': timestamp, 'PlaceID': place_id, 'AssetsLoaded': assets_loaded})

    return 'OK'


app.run(
    port=80,
    host="0.0.0.0"
)
