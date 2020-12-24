import requests
import json
import sys

def main():
    url = "http://kodi-wohnzimmer.fritz.box:8080/jsonrpc"
    #url = "http://192.168.2.30:8080/jsonrpc"
    #url = "http://192.168.1.94:8080/jsonrpc"

    # SAMPLE PARAMETERS Player.GetProperties time
    payload ={ "jsonrpc": "2.0", "method": sys.argv[1], "params": { "properties":[ sys.argv[2]], "playerid": 0 }, "id": 1 }    
    response = requests.post(url, json=payload).json()

    print(response)

if __name__ == "__main__":
    main()
