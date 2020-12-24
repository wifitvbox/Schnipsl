import requests
import json
import sys

def main():
    url = "http://192.168.1.127:8080/jsonrpc"
    #url = "http://kodiwohnzimmer.fritz.box:8080/jsonrpc"
    #url = "http://kodi-wohnzimmer.fritz.box:8080/jsonrpc"
    #url = "http://192.168.2.30:8080/jsonrpc"
    #url = "http://192.168.1.94:8080/jsonrpc"

    # Example echo method
    payload ={"jsonrpc":"2.0", "id":1, "method": "Player.Open", "params":{"item":{"file":sys.argv[1]}}}
    
    response = requests.post(url, json=payload).json()

    print(response)

if __name__ == "__main__":
    main()
