import json
from insite_plugin import InsitePlugin
from port_collector import PortCollector


class Plugin(InsitePlugin):
    def can_group(self):
        return False

    def fetch(self, hosts):

        host = hosts[-1]

        try:

            self.ipx

        except Exception:

            params = {"address": host, "ports": [1, 3, "5 - 9", 11, 15, "20 - 23"], "type": "NATX"}  # // OR "type": "IPX"

            self.ipx = PortCollector(**params)

        documents = []

        for _, params in self.ipx.collect.items():

            document = {"fields": params, "host": host, "name": "ipx"}

            documents.append(document)

        return json.dumps(documents)
