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

On the grafana interface use the Import feature to load the dashboard further down for an example.

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

Grafana dashboard
```JSON
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "collapsed": false,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 2,
      "panels": [],
      "title": "Station ${chargy_station}",
      "type": "row"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            }
          },
          "mappings": [],
          "unit": "none",
          "unitScale": true
        },
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 4,
        "x": 0,
        "y": 1
      },
      "id": 1,
      "options": {
        "displayLabels": [
          "name",
          "value"
        ],
        "legend": {
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true,
          "values": []
        },
        "pieType": "donut",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
          },
          "editorMode": "code",
          "expr": "sum by (chargy_connector_state)  (chargy_connector_state{station=\"${chargy_station}\"})",
          "instant": false,
          "legendFormat": "__auto",
          "range": true,
          "refId": "A"
        }
      ],
      "title": "Availability now",
      "type": "piechart"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "axisSoftMin": 0,
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 30,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": false,
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "normal"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "decimals": 0,
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "none",
          "unitScale": true
        },
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 20,
        "x": 4,
        "y": 1
      },
      "id": 3,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
          },
          "editorMode": "code",
          "expr": "sum by (chargy_connector_state)  (chargy_connector_state{station=\"${chargy_station}\"})",
          "instant": false,
          "legendFormat": "__auto",
          "range": true,
          "refId": "A"
        }
      ],
      "title": "Historic value",
      "type": "timeseries"
    },
    {
      "collapsed": false,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 10
      },
      "id": 4,
      "panels": [],
      "title": "Network",
      "type": "row"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            }
          },
          "mappings": [],
          "unit": "none",
          "unitScale": true
        },
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 4,
        "x": 0,
        "y": 11
      },
      "id": 5,
      "options": {
        "displayLabels": [
          "name",
          "value"
        ],
        "legend": {
          "displayMode": "table",
          "placement": "bottom",
          "showLegend": true,
          "values": [
            "value",
            "percent"
          ]
        },
        "pieType": "donut",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
          },
          "editorMode": "code",
          "expr": "sum by (chargy_connector_state)  (chargy_connector_state)",
          "instant": false,
          "legendFormat": "__auto",
          "range": true,
          "refId": "A"
        }
      ],
      "title": "Network Availability now",
      "type": "piechart"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "axisSoftMin": 0,
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 30,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": false,
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "normal"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unitScale": true
        },
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 20,
        "x": 4,
        "y": 11
      },
      "id": 6,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
          },
          "editorMode": "code",
          "expr": "sum by (chargy_connector_state)  (chargy_connector_state)",
          "instant": false,
          "legendFormat": "__auto",
          "range": true,
          "refId": "A"
        }
      ],
      "title": "Historic network value",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "continuous-YlBl"
          },
          "mappings": [],
          "max": 1,
          "min": 0,
          "thresholds": {
            "mode": "percentage",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "percentunit",
          "unitScale": true
        },
        "overrides": []
      },
      "gridPos": {
        "h": 7,
        "w": 4,
        "x": 0,
        "y": 20
      },
      "id": 7,
      "options": {
        "minVizHeight": 75,
        "minVizWidth": 75,
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true,
        "sizing": "auto"
      },
      "pluginVersion": "10.3.3",
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
          },
          "editorMode": "code",
          "expr": "count( sum by (station) (chargy_connector_state{chargy_connector_state=\"available\"}) == 0  ) / count( sum by (station) (chargy_connector_state) )",
          "instant": false,
          "legendFormat": "__auto",
          "range": true,
          "refId": "A"
        }
      ],
      "title": "Stations fully booked",
      "transformations": [],
      "type": "gauge"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "% of unavailable stations",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": false,
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "max": 1,
          "min": 0,
          "thresholds": {
            "mode": "percentage",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "percentunit",
          "unitScale": true
        },
        "overrides": []
      },
      "gridPos": {
        "h": 7,
        "w": 20,
        "x": 4,
        "y": 20
      },
      "id": 8,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": false
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "pluginVersion": "10.3.3",
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
          },
          "editorMode": "code",
          "expr": "count( sum by (station) (chargy_connector_state{chargy_connector_state=\"available\"}) == 0  ) / count( sum by (station) (chargy_connector_state) )",
          "instant": false,
          "legendFormat": "__auto",
          "range": true,
          "refId": "A"
        }
      ],
      "title": "Evolution of stations fully booked",
      "transformations": [],
      "type": "timeseries"
    }
  ],
  "refresh": "5m",
  "schemaVersion": 39,
  "tags": [],
  "templating": {
    "list": [
      {
        "current": {
          "selected": false,
          "text": "Schuttrange - Parking Eglise",
          "value": "Schuttrange - Parking Eglise"
        },
        "datasource": {
          "type": "prometheus",
          "uid": "b76be717-ff33-41f6-a2df-696bdf2b9e29"
        },
        "definition": "label_values(station)",
        "hide": 0,
        "includeAll": false,
        "label": "Station",
        "multi": false,
        "name": "chargy_station",
        "options": [],
        "query": {
          "query": "label_values(station)",
          "refId": "PrometheusVariableQueryEditor-VariableQuery"
        },
        "refresh": 1,
        "regex": "",
        "skipUrlSync": false,
        "sort": 0,
        "type": "query"
      }
    ]
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Station View",
  "uid": "fe32b694-6cf6-40c8-a5df-3dac157eab5e",
  "version": 26,
  "weekStart": ""
}
```
