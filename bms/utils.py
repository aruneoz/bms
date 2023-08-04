from google.cloud.logging.handlers import CloudLoggingHandler
from google.cloud.logging_v2.handlers import setup_logging
# explicitly set up a CloudLoggingHandler to send logs over the network
import google.cloud.logging

client = google.cloud.logging.Client()
import logging

# Instantiates a client


handler = CloudLoggingHandler(client)
setup_logging(handler)

def write_logs(level, msg):
    if level == 'warning':
        logging.warning(msg)
    elif level == 'error':
        logging.error(msg)
    elif level == 'debug':
        logging.debug(msg)
    else:
        logging.info(msg)

