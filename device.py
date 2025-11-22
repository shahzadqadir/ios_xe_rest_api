# ~/automation/rest_api/device.py
import requests
import os
from requests.auth import HTTPBasicAuth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CiscoDevice:
    def __init__(self, hostname: str, username: str, password: str):
        self.base_url = f"https://{hostname}/restconf/data"
        self.username = username
        self.password = password
        self.headers = {
            "Accept": "application/yang-data+json",
            "Content-Type": "application/yang-data+json",
            }

    def get_interfaces_json(self):
        response = requests.get(
            url=f"{self.base_url}/Cisco-IOS-XE-native:native/interface",
            headers=self.headers,
            auth=HTTPBasicAuth(username=self.username, password=self.password),
            verify=False
            )
        return response.json()
    
    def print_gig_interfaces(self):
        try:
            result = self.get_interfaces_json()
            interfaces = result['Cisco-IOS-XE-native:interface']
            gig_interfaces = interfaces['GigabitEthernet']
            for interface in gig_interfaces:
                print(interface)
        except KeyError:
            print("No GigabitEthernet interfaces found.")

    def print_loopback_interfaces(self):
        try:
            result = self.get_interfaces_json()
            interfaces = result['Cisco-IOS-XE-native:interface']
            loopback_interfaces = interfaces['Loopback']
            for interface in loopback_interfaces:
                print(interface)  
        except KeyError:
            print("No Loopback Interfaces found.")

    def add_update_loopback_interface(self, ipaddr: str, mask: str, name: str, descr: str, update:bool=False):
        payload = {
            "Cisco-IOS-XE-native:Loopback": [
                {
                    "name": int(name),
                    "description": f"{descr}",
                    "ip": {
                        "address": {
                            "primary": {
                                "address": ipaddr,
                                "mask": mask
                                }
                            }
                        }
                    }
                ]
            }
        if update:
            response = requests.put(
            url=f"{self.base_url}/Cisco-IOS-XE-native:native/interface/Loopback={name}",
            json=payload,
            headers=self.headers,
            auth=HTTPBasicAuth(username=self.username, password=self.password),
            verify=False
            )
        else:
            response = requests.post(
                url=f"{self.base_url}/Cisco-IOS-XE-native:native/interface",
                json=payload,
                headers=self.headers,
                auth=HTTPBasicAuth(username=self.username, password=self.password),
                verify=False
                )
        return response
    
    def get_static_routes_json(self):        
        response = requests.get(
            url=f"{self.base_url}/Cisco-IOS-XE-native:native/ip/route",
            headers=self.headers,
            auth=HTTPBasicAuth(username=self.username, password=self.password),
            verify=False
            )
        if response.status_code == 204:
            return []
        return response.json()
    
    def print_static_routes(self):
        result = self.get_static_routes_json()
        if len(result) > 0:
            routes = result['Cisco-IOS-XE-native:route']
            static_routes_list = routes['ip-route-interface-forwarding-list']
            for route in static_routes_list:
                print(route)
        else:
            print("No static routes defined.")

    def add_static_route(self, destination: str, mask: str, next_hop: str):
        url = f"{self.base_url}/Cisco-IOS-XE-native:native/ip/route/"

        payload = {
            "Cisco-IOS-XE-native:ip-route-interface-forwarding-list": {
                "prefix": destination,
                "mask": mask,
                "fwd-list": [
                    {"fwd": next_hop}
                ]
            }
        }

        response = requests.post(
            url=url,
            json=payload,
            headers=self.headers,
            auth=HTTPBasicAuth(self.username, self.password),
            verify=False
        )

        return response

    def delete_static_route(self, destination: str, mask: str):
        url = f"{self.base_url}/Cisco-IOS-XE-native:native/ip/route/ip-route-interface-forwarding-list={destination},{mask}"

        response = requests.delete(
            url=url,
            headers=self.headers,
            auth=HTTPBasicAuth(self.username, self.password),
            verify=False
            )

        return response  
    

def main():
    device = CiscoDevice("10.10.99.1", "script", "cisco123")
    result = device.delete_static_route("10.10.100.0", "255.255.255.0")
    if result.status_code == 204:
        print("Static Route deleted successfuly")
    else:
        print(result)

if __name__ == "__main__":
    main()