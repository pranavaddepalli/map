import json
import csv
import os

folder_path = "Location History (Timeline)/Semantic Location History/2023"
placevisits = []

for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            for obj in data['timelineObjects']:
                if 'placeVisit' in obj:
                    placevisits.append(obj['placeVisit'])

placevisits.sort(key=lambda x: x['duration']['startTimestamp'])

markers_csv_file_path = "markers_output.csv"
lines_csv_file_path = "lines_output.csv"

num = 0
previous_location = None  # To store the coordinates of the previous location

# Write markers to the markers CSV file
with open(markers_csv_file_path, 'w', newline='') as markers_csv_file:
    fieldnames_markers = ['name', 'address', 'longitude', 'latitude', 'number', 'WKT', 'startTimestamp', 'endTimestamp']
    csv_writer_markers = csv.DictWriter(markers_csv_file, fieldnames=fieldnames_markers)

    csv_writer_markers.writeheader()

    for location in placevisits:
        duration = location['duration']
        startTimestamp = duration['startTimestamp']
        endTimestamp = duration['endTimestamp']
        location = location['location']
        name = location.get('name', 'no name')
        address = location.get('address', '')
        longitude = location['longitudeE7'] / 1e7
        latitude = location['latitudeE7'] / 1e7
        num += 1

        # Create WKT Point geometry format for markers
        wkt_point = f"POINT ({longitude} {latitude})"
        csv_writer_markers.writerow({
            'name': name,
            'address': address,
            'longitude': longitude,
            'latitude': latitude,
            'number': num,
            'WKT': wkt_point,
            'startTimestamp': startTimestamp,
            'endTimestamp': endTimestamp
        })

# Write lines to the lines CSV file
with open(lines_csv_file_path, 'w', newline='') as lines_csv_file:
    fieldnames_lines = ['name', 'address', 'longitude', 'latitude', 'number', 'WKT']
    csv_writer_lines = csv.DictWriter(lines_csv_file, fieldnames=fieldnames_lines)

    csv_writer_lines.writeheader()

    for location in placevisits:
        location = location['location']
        name = location.get('name', 'no name')
        longitude = location['longitudeE7'] / 1e7
        latitude = location['latitudeE7'] / 1e7
        num += 1

        if previous_location:
            # Create WKT LineString geometry format for lines
            wkt_line = f"LINESTRING ({previous_location['longitude']} {previous_location['latitude']}, {longitude} {latitude})"
            csv_writer_lines.writerow({
                'name': f"Line between {previous_location['name']} and {name}",
                'address': '',
                'longitude': '',
                'latitude': '',
                'number': '',
                'WKT': wkt_line
            })

        # Update the previous_location for the next iteration
        previous_location = {'name': name, 'longitude': longitude, 'latitude': latitude}

print(f"Markers CSV file written to {markers_csv_file_path}")
print(f"Lines CSV file written to {lines_csv_file_path}")
