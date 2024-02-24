import os
from time import sleep
from chargy import ChargyData
from prometheus_client import start_http_server, Enum
from prometheus_client.core import REGISTRY
from prometheus_client.registry import Collector
from prometheus_client.metrics_core import StateSetMetricFamily,InfoMetricFamily

class ChargyCollector(Collector):

    def __init__(self,chargy):
        self.chargy = chargy

    def collect(self):

        #Update chargydata only if needed
        self.chargy.reload(expired_only=True)

        #Define Metrics
        m_state_simple = StateSetMetricFamily('chargy_connector_state','State of chargy device connector',labels=("connector","device","station","speed") )
        m_state_detailed = InfoMetricFamily('chargy_connector_detailed_state','Exact state of chargy device connector',labels=("connector","device","station","speed") )
        

        #Iterate through all connectors
        for station in self.chargy.stations:
            for device in station.devices:
                for connector in device.connectors:
                    m_state_simple.add_metric( ( connector.name, device.name, station.name, str(connector.speed) ) , value={state: state == connector.state for state in connector.STATES} )
                    m_state_detailed.add_metric( ( connector.name, device.name, station.name, str(connector.speed) ) , value={"state":connector.state_detailed} )

        #Return counters
        yield m_state_simple
        yield m_state_detailed

"""
        c = InfoMetricFamily("health", "Health Monitoring")
        c.add_metric(labels=name, value={"name": name, "status": status, "value": value})

        #See example: https://github.com/torsdag/eggbasket/blob/ebb95d18954040908c064d000c75ff16151fb593/source/eggbasket/collector.py#L5
        client_state = StateSetMetricFamily(
            "active_licenses", "active license count", labels=("host", "port", "license", "user")
        )        
        for license in self._licenses:
            license_counter.add_metric(
                [license.name], len(license.licenses)
            )

            for client in license.licenses:
                client_state.add_metric(
                    (client.host, str(client.port), license.name, client.user), value={"active": True}
                )

        service_states = StateSetMetricFamily(
            'pyca_service_state_info',
            'Service State of pyCA processes',
            labels=['service', 'state']
        )

        for service in Service.values():
            c = CounterMetricFamily('my_counter_total', 'Help text', labels=['foo'])
            service_states.add_metric(
                [Service.str(service)],
                self.get_state_dict(get_service_status(service))
            )
"""

        


##
## Startup Prometheus Exporter
##
if __name__ == '__main__':

    # kml_url from env
    kml_url = os.getenv("KML_URL")
    if not kml_url: raise ValueError("Missing environment variable KML_URL")
    
    # Start up the server to expose the metrics.
    start_http_server(9000)

    #Launch data publisher
    chargy=ChargyData(url=kml_url)
    REGISTRY.register(ChargyCollector(chargy))

    #Wait forever to let metrics server work
    while True:
        sleep(1)

