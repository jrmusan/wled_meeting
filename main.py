import requests
import pprint

# So the plan is to check for www.google-meet.com as an open tab

# If its found we need to

    # First get current state of WLED's and store it
    # Set them to red
        # Keep checking if the tab is open or not



url = 'http://nanoleaf.local/json/state'

# json = {"on":"t","seg":[{"col":[[0,255,200]]}]}
json = {
    "seg":[{
        "col":[[207,8,8]]
        }]
    }

header = {'Content-Type': 'application/json'}

response = requests.post(url=url, headers=header, json=json)

print(response)

pprint.pprint(response.json())

