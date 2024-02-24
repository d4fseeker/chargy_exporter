# chargy_exporter
Prometheus Exporter for the luxembourgish Chargy public EV charger network


## Usage

This repository provides the Dockerfile and source code to build the chargy_exporter docker container.
There are currently no plans to provide prebuilt dockerhub containers due to automatic rebuilds being a subscription feature and the risk of security issues increasing with the age of containers.

The API Link and Key used below are provided through the OpenData initiative of the luxembourgish government. The link, API-key and data access license are subject to changes by the provider.
Please see: https://data.public.lu/en/datasets/bornes-de-chargement-publiques-pour-voitures-electriques/

### Basic Usage

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
