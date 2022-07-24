import requests
import pprint


url = 'http://nanoleaf.local/json/state'
header = {'Content-Type': 'application/json'}

# response = requests.post(url=url, headers=header, json=json)
# response = requests.get(url=url, headers=header)
# pprint.pprint(response.json())


def is_on():
    """
    Checks if the nanoleaf is on or not

    Returns:
        bool: True if the light is on
    """

    response = requests.get(url=url, headers=header)
    info = response.json()

    if response.ok:
        return info['on']
    else:
        raise Exception("Nanolights not responding")


def in_meeting():
    """
    First check if the nanolefs are on, if so get its current status.
    If its not on just turn it on and set it to red. 
    """

    if is_on:
        #~~~~~~~~~~This is where we SOMEHOW have to get its current status~~~~~~~~~~
        print("Lights are already on, setting to red")

        # For now, we are just setting them red either way...
        set_red()
    else:
        # Lights aren't on, just set to red, who cares what they were before? I sure don't
        set_red(True)


def set_red(turn_on=False):
    """
    Sets em red
    """
    
    payload = {}

    if not is_on():
        payload["on"] = "t"

    # Set em to red
    payload["seg"] = {"i":[0,600,[255,0,0]]}
            
    response = requests.post(url=url, headers=header, json=payload)
    if not response.ok:
        raise Exception("Nanolights not responding")


def set_green(turn_on=False):
    """
    Sets em green
    """
    
    payload = {}

    if not is_on():
        payload["on"] = "t"

    # Set em to red
    payload["seg"] = {"i":[0,600,[0,128,0]]}
            
    response = requests.post(url=url, headers=header, json=payload)
    if not response.ok:
        raise Exception("Nanolights not responding")