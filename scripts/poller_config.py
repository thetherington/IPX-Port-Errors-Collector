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

            params = {"address": host, "ports": [1, 3, 5, 7, 9, 11, 15, 20, 23, 25, 30]}

            self.ipx = PortCollector(**params)

        documents = []

        for port in self.ipx.collect():

            document = {"fields": port, "host": host, "name": "ipx"}

            documents.append(document)

        return json.dumps(documents)
