# chargy_exporter
Prometheus Exporter for the luxembourgish Chargy public EV charger network


## Preamble

### No prebuilts
This repository provides the Dockerfile and source code to build the chargy_exporter docker container.
There are currently no plans to provide prebuilt dockerhub containers due to automatic rebuilds being a subscription feature and the risk of security issues increasing with the age of containers.

### Data access
The API Link and Key used below are provided through the OpenData initiative of the luxembourgish government. The link, API-key and data access license are subject to changes by the provider.
Please see: https://data.public.lu/en/datasets/bornes-de-chargement-publiques-pour-voitures-electriques/

### License
This code is licensed under MPL-2.0. Any derivative work and commercial usage within the bounds of the license are encouraged.

### Data Refreshing
The API provides new data every 5min. 
To reduce load on the API servers and prevent getting kicked off, we cache the KML data for 5min.
To reduce unnecessary data storage on Prometheus, we scrape the exporter every 5min.
This means that worst-case the data is already 5min + 5min + 5min  = 15min old when it is being stored. This is considered acceptable for my use cases and the current stack and API does not permit to improve this significantly without significant drawbacks in storage capacity or network.

## Usage

### Query format
The exporter iterates over each Chargy station --> Chargy device --> Chargy connector to provides the state metrics `chargy_connector_state` and info metrics `chargy_connector_detailed_state_info` per connector.
A chargy station is identified by the location (.e.g the name of a Parking).
A chargy device is the actual device your car is being connected to
A chargy connector is the port/cable on the chargy device. A device can have 1-to-n connectors (but usually has 2).

#### chargy_connector_state

 
`chargy_connector_state`:  A simplified state list, the current connector state is on value 1, the other states are 0. Valid states are: [ "available","charging","unavailable" ]

`connector`: Name of the connector, usually the device name followed by the connector number.

`device`: Name of the device

`station`: Name of the station/parking/location/... which contains the Chargy device

`speed`: Max speed in kWh provided by this station. Most standard stations are 22kW


#### chargy_connector_detailed_state_info

`chargy_connector_detailed_state_info`:  The actual state as provided by the network for the station. A list of all known states is available in the file src/chargy.py

`connector`: Name of the connector, usually the device name followed by the connector number.

`device`: Name of the device

`station`: Name of the station/parking/location/... which contains the Chargy device

`speed`: Max speed in kWh provided by this station. Most standard stations are 22kW

### Example query

Sum the chargers of a given station by current state:
```PromQL
sum by (chargy_connector_state)  (chargy_connector_state{station="${chargy_station}"})
```

Sum the availability across the entire network:
```
sum by (chargy_connector_state)  (chargy_connector_state)
```

Percentage of stations with no charger available:
```
count( sum by (station) (chargy_connector_state{chargy_connector_state="available"}) == 0  ) / count( sum by (station) (chargy_connector_state) )
```

## Getting started

To build and run a docker container
```bash
git clone https://github.com/d4fseeker/chargy_exporter.git
docker build chargy_exporter -t chargy_exporter:latest
docker run -d --name chargy_exporter -p 9000:9000 -e "KML_URL=https://my.chargy.lu/b2bev-external-services/resources/kml?API-KEY=486ac6e4-93b8-4369-9c6a-28f7c4e1a81f" chargy_exporter:latest
```

Access the Prometheus-style exporter URL:
http://<your_host_ip>:9000/

#### Example Docker-Compose Stack
A full-featured demo stack consisting of the chargy_exporter, Prometheus engine and Grafana webinterface.
Save the files below to a new folder. Then run "docker compose up -d".
Using your browser you will be able to reach:
- http://<YOUR_HOST_IP>:9000 to check chargy_exporter working
- http://<YOUR_HOST_IP>:9090 to access the Prometheus engine
- http://<YOUR_HOST_IP>:3000 to access Grafana

On the grafana interface use the Import feature to load the dashboard linked here:
https://github.com/d4fseeker/chargy_exporter/files/14392863/grafana_dashboard.json

Dashboard screenshot:
![chargy_grafana](https://github.com/d4fseeker/chargy_exporter/assets/287879/3478c4a2-15fe-407f-8c7e-4c04ef4085f9)

File docker-compose.yml
```YAML
#Docker-Compose version. Do not change
version: '3.9'


services:

  ## chargy_exporter
  chargy_exporter:
    build: app/chargy_exporter
    user: '1001:0'
    environment:
      - KML_URL=https://my.chargy.lu/b2bev-external-services/resources/kml?API-KEY=486ac6e4-93b8-4369-9c6a-28f7c4e1a81f
    ports:
      - '9000:9000'

  ## Prometheus
  prometheus:
    image: prom/prometheus:latest
    restart: always
    volumes:
      - './data/prometheus:/prometheus'
      - './config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml'
    ports:
      - '9090:9090'
    command:
      #Defaults extracted from running container
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      #Custom options
      - '--storage.tsdb.retention.time=2y'

  ## Grafana
  grafana:
    image: grafana/grafana:latest
    restart: always
    container_name: grafana
    ports:
      - '3000:3000'
    volumes:
      - './data/grafana:/var/lib/grafana'
```

File config/prometheus/prometheus.yml  (Change YOUR_HOST_NAME in targets)
```YAML
global:
  scrape_interval:     15s # By default, scrape targets every 15 seconds.
  external_labels:
    monitor: 'chargy_prometheus'
scrape_configs:
  - job_name: 'chargy_exporter'
    scrape_interval: 5m
    static_configs:
      - targets: ['YOUR_HOST_NAME:9000']
```
