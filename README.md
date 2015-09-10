Druid metrics collector
===
A simple HTTP server that forwards Druid metrics to a Kafka topic or a statsd server.


Druid's HTTP emitter sends a batch of metrics to the HTTP endpoint. They typically look like this :

```
[
{"feed": "metrics", "user2": "Code Cache", "service": "middlemanager", "user1": "nonheap", "timestamp": "2015-04-22T19:31:17.685Z", "metric": "jvm/pool/max", "value": 50331648, "host": "middlemanager:8089"},
{"feed": "metrics", "user2": "Code Cache", "service": "middlemanager", "user1": "nonheap", "timestamp": "2015-04-22T19:31:17.685Z", "metric": "jvm/pool/max", "value": 50331648, "host": "middlemanager:8089"}
.....
]
```

Install
---
```
apt-get update
apt-get install -y python-pip
pip install -r requirements.txt
```

Run with kafka endpoint
---
1. `druid-metrics-collector.py --endpoint=kafka --broker_list=<broker_list> --kafka_topic=<kafka_topic> [--host=<socket_host>] [--port=<socket_port>]`
2. Configure druid to send to the `http://<host>:<port>/metrics` endpoint.

Run with statsd endpoint
---
1. `druid-metrics-collector.py [--endpoint=statsd] [--statsd_host=<statsd_host>] [--statsd_port=<statsd_port>] [--host=<socket_host>] [--port=<socket_port>]`
2. Configure druid to send to the `http://<host>:<port>/metrics` endpoint.

Test
---
```
curl -XPOST localhost:9999/metrics -H "Content-Type: application/json" -d '[{"feed": "metrics", "user2": "Code Cache", "service": "middlemanager", "user1": "nonheap", "timestamp": "2015-04-22T19:31:17.685Z", "metric": "jvm/pool/max", "value": 50331648, "host": "middlemanager:8089"},{"feed": "metrics", "user2": "Code Cache", "service": "middlemanager", "user1": "nonheap", "timestamp": "2015-04-22T19:31:17.685Z", "metric": "jvm/pool/max", "value": 50331648, "host": "middlemanager:8089"}]'
```
