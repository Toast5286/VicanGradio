import json
import sys
path = sys.argv[1]

# Load the data from the JSON file
with open(path, 'r') as f:
    data = json.load(f)

# Get the data for object 55
object_55_data = data['0']

# Replicate object 55 data for objects 56 to 88
for i in range(1, 21):
    data[str(i)] = object_55_data

# Write the updated data back to the JSON file
with open(path, 'w') as f:
    json.dump(data, f, indent=4)