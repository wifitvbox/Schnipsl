import requests
import json
import sys

def main():
    url = "http://kodi-wohnzimmer.fritz.box:8080/jsonrpc"
    #url = "http://192.168.2.30:8080/jsonrpc"
    #url = "http://192.168.1.94:8080/jsonrpc"

    # Example echo method
    payload ={ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "params": { "filter": { "id": sys.argv[1], "type": "method" } }, "id": 1 }    
    response = requests.post(url, json=payload).json()

    print(response)

if __name__ == "__main__":
    main()
