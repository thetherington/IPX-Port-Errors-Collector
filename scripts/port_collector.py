import copy
import json

import requests


class PortCollector:
    def __init__(self, **kwargs):

        self.address = None

        self.input_error = {"id": "926.<replace>@i", "type": "integer", "name": "l_input_errors"}
        self.output_error = {"id": "931.<replace>@i", "type": "integer", "name": "l_output_errors"}
        self.port_label = {"id": "344.<replace>@s", "type": "string", "name": "s_label"}
        self.port_status = {"id": "921.<replace>@i", "type": "integer", "name": "s_operation_status"}

        self.parameters = []

        self.port_store = {}

        self.fetch = self.fetch_ipx

        for key, value in kwargs.items():

            if "address" in key and value:
                self.address = value

            if "ports" in key and value:

                port_list = []
                for port in value:

                    if isinstance(port, str) and "-" in port:

                        start, stop = port.split("-")
                        port_list.extend(list(range(int(start), int(stop) + 1)))

                    else:
                        port_list.append(port)

                port_list = list(set(port_list))

                for port in port_list:

                    for template in [self.input_error, self.output_error, self.port_label, self.port_status]:

                        template_copy = copy.deepcopy(template)
                        template_copy["id"] = template_copy["id"].replace("<replace>", str(port - 1))

                        self.parameters.append(template_copy)

            if "type" in key and value:

                if value == "NATX":
                    self.fetch = self.fetch_natx

    def fetch_ipx(self, parameters):

        try:

            with requests.Session() as session:

                ## get the session ID from accessing the login.php site
                resp = session.get(
                    "http://%s/login.php" % self.address,
                    verify=False,
                    timeout=30.0,
                )

                sessionID = resp.headers["Set-Cookie"].split(";")[0]

                payload = {
                    "jsonrpc": "2.0",
                    "method": "get",
                    "params": {"parameters": parameters},
                    "id": 1,
                }

                url = "http://%s/cgi-bin/cfgjsonrpc" % (self.address)

                headers = {
                    "content_type": "application/json",
                    "Cookie": sessionID + "; webeasy-loggedin=true",
                }

                response = session.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload),
                    verify=False,
                    timeout=30.0,
                )

                return json.loads(response.text)

        except Exception as error:
            print(error)
            return error

    def fetch_natx(self, parameters):

        try:

            with requests.Session() as session:

                session.auth = ("root", "evertz")

                payload = {
                    "jsonrpc": "2.0",
                    "method": "get",
                    "params": {"parameters": parameters},
                    "id": 1,
                }

                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                url = "http://%s/v.1.5/php/datas/cfgjsonrpc.php" % (self.address)

                response = session.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload),
                    verify=False,
                    timeout=30.0,
                )

                return json.loads(response.text)

        except Exception as error:
            print(error)
            return error

    @property
    def collect(self):

        results = self.fetch(self.parameters)

        ports = {}

        for result in results["result"]["parameters"]:

            try:

                # seperate "240.1@i" to "1@i"
                _id = result["id"].split(".")[1]

                # split the instance and type notation, then convert the
                # instance back to base 1 for port number
                _instance = _id.split("@")[0]
                _instance = int(_instance) + 1

                key = result["name"]

                if "operation_status" in key:

                    lookup = {0: "UP", 1: "DOWN"}
                    result["value"] = lookup[result["value"]]

                # create port key and object if doesn't exist, otherwise update existing key/object
                if _instance not in ports.keys():

                    ports.update(
                        {
                            _instance: {
                                key: result["value"],
                                "as_id": [result["id"]],
                                "i_port": _instance,
                            }
                        }
                    )

                else:

                    ports[_instance].update({key: result["value"]})
                    ports[_instance]["as_id"].append(result["id"])

            except Exception as error:
                print(error)

        for port_key, params in ports.items():

            try:

                # if port object exists in port_store, then update ports dict with delta values
                if port_key in self.port_store.keys():

                    for key in ["l_input_errors", "l_output_errors"]:

                        x = params[key]
                        y = self.port_store[port_key][key]

                        params.update({"{}_delta".format(key): x - y if x > y else 0})

                    # update object in port_store with latest values
                    self.port_store[port_key].update(params)

                else:

                    # create a port object into port_store keyed by the port number
                    self.port_store.update({port_key: params})

            except Exception as error:
                print(error)

        return ports


def main():

    params = {"address": "172.16.140.62", "ports": [1, 3, "5 - 9", 11, 15, "20 - 23"], "type": "NATX"}

    ipx = PortCollector(**params)

    input_quit = False

    while input_quit is not "q":

        for _, items in ipx.collect.items():

            print(json.dumps(items, indent=1))

        input_quit = input("\nType q to quit or just hit enter: ")


if __name__ == "__main__":
    main()
