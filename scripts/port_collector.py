import copy
import json

import requests


class PortCollector:
    def __init__(self, **kwargs):

        self.address = None

        self.input_error = {"id": "926.<replace>@i", "type": "integer", "name": "Input Errors"}
        self.output_error = {"id": "931.<replace>@i", "type": "integer", "name": "Output Errors"}
        self.port_label = {"id": "344.<replace>@s", "type": "string", "name": "Label"}

        self.parameters = []

        for key, value in kwargs.items():

            if "address" in key and value:
                self.address = value

            if "ports" in key and value:

                for port in value:

                    for template in [self.input_error, self.output_error, self.port_label]:

                        template_copy = copy.deepcopy(template)
                        template_copy["id"] = template_copy["id"].replace(
                            "<replace>", str(port - 1)
                        )

                        self.parameters.append(template_copy)

    def fetch(self, parameters):

        try:

            with requests.Session() as session:

                ## get the session ID from accessing the login.php site
                resp = session.get(
                    "http://%s/login.php" % self.address, verify=False, timeout=30.0,
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
                    url, headers=headers, data=json.dumps(payload), verify=False, timeout=30.0,
                )

                return json.loads(response.text)

        except Exception as error:
            print(error)
            return error

    def collect(self):

        results = self.fetch(self.parameters)

        ports = {}

        try:

            for result in results["result"]["parameters"]:

                # seperate "240.1@i" to "1@i"
                _id = result["id"].split(".")[1]

                # split the instance and type notation, then convert the
                # instance back to base 1 for port number
                _instance, _type = _id.split("@")

                _instance = int(_instance)
                _instance += 1

                # convert integer to long notation since these numbers can be big
                _type = "l" if _type == "i" else _type

                # create port key and object if doesn't exist, otherwise update existing key/object
                if _instance not in ports.keys():

                    ports.update(
                        {
                            _instance: {
                                _type
                                + "_"
                                + result["name"].lower().replace(" ", "_"): result["value"],
                                "as_id": [result["id"]],
                            }
                        }
                    )

                else:

                    ports[_instance].update(
                        {_type + "_" + result["name"].lower().replace(" ", "_"): result["value"]}
                    )

                    ports[_instance]["as_id"].append(result["id"])

        except Exception as error:
            print(error)

        for _, params in ports.items():

            yield params


def main():

    params = {"address": "172.16.140.14", "ports": [1, 3, 5, 7, 9, 11, 15, 20, 23, 25, 30]}

    ipx = PortCollector(**params)

    for port in ipx.collect():

        print(json.dumps(port, indent=1))


if __name__ == "__main__":
    main()
