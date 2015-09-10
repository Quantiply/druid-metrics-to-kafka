"""
 Copyright 2014-2015 Quantiply Corporation. All rights reserved.
 
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
 
      http://www.apache.org/licenses/LICENSE-2.0
 
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

Usage:
  druid-metrics-collector.py [--endpoint=<endpoint>] [--statsd_host=<statsd_host>] [--statsd_port=<statsd_port>] [--broker_list=<broker_list>] [--kafka_topic=<kafka_topic>] [--host=<socket_host>] [--port=<socket_port>]
"""
from docopt import docopt

import cherrypy
import json
import statsd

from kafka.client import KafkaClient
from kafka.producer import SimpleProducer
import logging


class KafkaMetrics(object):
    
    def __init__(self, broker_list, kafka_topic):
        logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('druid-kafka-metrics')
        self.log.info("Kafka (brokers=%s, topic=%s)" %(broker_list, kafka_topic))
        client = KafkaClient(broker_list)
        self.producer = SimpleProducer(client)
        self.msg_count = 0
        self.kafka_topic = kafka_topic
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def metrics(self):
        messages = cherrypy.request.json

        for message in messages:
            self.msg_count += 1
            self.log.debug("%s - %s" % (self.msg_count, str(message)))
            self.producer.send_messages(self.kafka_topic, json.dumps(message))

            if self.msg_count % 100 == 0 :
                self.log.info("%s messages processed." % (self.msg_count, ))

        return "{'code':200}"

class StatsdMetrics(object):

    def __init__(self, statsd_host, statsd_port):
        logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('druid-statsd-metrics')
        self.log.info("Statsd (host=%s, port=%s)" %(statsd_host, statsd_port))
        self.s_conn = statsd.StatsClient(host=statsd_host, port=statsd_port)
        self.msg_count = 0

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()

    def metrics(self):
        messages = cherrypy.request.json

        for message in messages:
        metric_name = message['service'] + '_' + message['metric'].replace('/','_')
        metric_value = message['value']
        self.s_conn.set(metric_name,metric_value)
            self.msg_count += 1
            self.log.debug("%s - %s" % (self.msg_count, str(message)))

            if self.msg_count % 100 == 0 :
                self.log.info("%s messages processed." % (self.msg_count, ))

        return "{'code':200}"
 

if __name__ == '__main__':    
    arguments = docopt(__doc__, version='0.1.1rc')
    BROKER_LIST = arguments['--broker_list'] or ''
    SOCKET_PORT = int(arguments['--port'] or 9999)
    SOCKET_HOST = arguments['--host'] or '0.0.0.0'
    TOPIC       = arguments['--kafka_topic'] or "druid-metrics"
    STATSD_HOST = arguments['--statsd_host'] or '127.0.0.1'
    STATSD_PORT = int(arguments['--statsd_port'] or 8125)
    ENDPOINT    = arguments['--endpoint'] or 'statsd'

    cherrypy.config.update({'server.socket_port': SOCKET_PORT})
    cherrypy.config.update({'server.socket_host': SOCKET_HOST})

    if ENDPOINT == 'kafka':
        cherrypy.quickstart(KafkaMetrics(BROKER_LIST, TOPIC))
    elif ENDPOINT == 'statsd':
        cherrypy.quickstart(StatsdMetrics(STATSD_HOST, STATSD_PORT))
