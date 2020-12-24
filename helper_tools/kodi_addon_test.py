import requests
import json
import sys
import base64

def main():
    url = "http://192.168.1.127:8080/jsonrpc"
    #url = "http://kodiwohnzimmer.fritz.box:8080/jsonrpc"
    #url = "http://kodi-wohnzimmer.fritz.box:8080/jsonrpc"
    #url = "http://192.168.2.30:8080/jsonrpc"
    #url = "http://192.168.1.94:8080/jsonrpc"

    # Example echo method
 
    #payload ={"jsonrpc":"2.0", "id":1, "method": "Player.Open", "params":{"item":{"file":sys.argv[1]}}}


    payload ={"jsonrpc":"2.0","method":"Addons.ExecuteAddon","params":{"addonid":"script.hello.world", "params" : [base64.urlsafe_b64encode(sys.argv[1].encode())]},"id":1}
    
    response = requests.post(url, json=payload).json()

    print(response)

if __name__ == "__main__":
    main()
