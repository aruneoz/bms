import json
import traceback
from concurrent.futures._base import TimeoutError
import os

from google.oauth2 import service_account
from google.pubsub_v1 import PubsubMessage
from google.cloud.pubsublite.cloudpubsub import SubscriberClient, PublisherClient
from google.cloud.pubsublite.types import (
    CloudRegion,
    CloudZone,
    FlowControlSettings,
    MessageMetadata,
    SubscriptionPath, TopicPath,
)

from bms import utils,batterypack_simulator

# TODO(developer):

project_number = os.environ.get('project_number')
#project_number = 779370283097
#cloud_region = "us-central1"
cloud_region = os.environ.get('cloud_region')
#subscription_id = "initializeBatteryReqSub"
subscription_id = os.environ.get('subscription_id')
#subscription_power_id= "batteryPowerReqSub"
subscription_power_id = os.environ.get('subscription_power_id')
#power_allocate_status_topic_id = "svp.simulation.battery.status"
power_allocate_status_topic_id = os.environ.get('power_allocate_status_topic_id')
#timeout = 90
timeout = os.environ.get('timeout')
#regional = True
regional = os.environ.get('regional')

location = CloudRegion(cloud_region)


subscription_path = SubscriptionPath(project_number, location, subscription_id)
power_topic_path = TopicPath(project_number, location, power_allocate_status_topic_id)
subscription_path_allocate_power = SubscriptionPath(project_number, location, subscription_power_id)


# Configure when to pause the message stream for more incoming messages based on the
# maximum size or number of messages that a single-partition subscriber has received,
# whichever condition is met first.
per_partition_flow_control_settings = FlowControlSettings(
    # 1,000 outstanding messages. Must be >0.
    messages_outstanding=1000,
    # 10 MiB. Must be greater than the allowed size of the largest message (1 MiB).
    bytes_outstanding=10 * 1024 * 1024,
)


def callback_allocate_power(message: PubsubMessage):
    try:
        message_data = message.data.decode("utf-8")
        metadata = MessageMetadata.decode(message.message_id)
        print(
            f"Received {message_data} of ordering key {message.ordering_key} with id {metadata}."
        )
        y = json.loads(message_data)

        utils.write_logs("info",
                         f"Received {message_data} of ordering key {message.ordering_key} with id {metadata}.")

        res = batterypack_simulator.allocate_power(y["power"])

        utils.write_logs("info",
                         f"Remaining Power Left  {res}.")

        with PublisherClient() as power_publisher_client:
            data = res
            api_future = power_publisher_client.publish(power_topic_path, data.encode("utf-8"))
            # result() blocks. To resolve API futures asynchronously, use add_done_callback().
            message_id = api_future.result()
            message_metadata = MessageMetadata.decode(message_id)
            print(
                f"Published a message to {power_topic_path} with partition {message_metadata.partition.value} and offset {message_metadata.cursor.offset}."
            )



    except Exception as e:
        traceback.print_exc()
        utils.write_logs("error",
                         f"Received {message_data} with exception {e}.")
    message.ack()


def callback(message: PubsubMessage):
    try:
        message_data = message.data.decode("utf-8")
        metadata = MessageMetadata.decode(message.message_id)
        print(
            f"Received {message_data} of ordering key {message.ordering_key} with id {metadata}."
        )
        y = json.loads(message_data)

        utils.write_logs("info",
                         f"Received {message_data} of ordering key {message.ordering_key} with id {metadata}.")

        res=batterypack_simulator.init_batterypack(y["batteryPacks"])

        utils.write_logs("info",
                         f"Loaded the Battery Pack Successfully  {res}.")

    except Exception as e1:
        traceback.print_exc()
        utils.write_logs("error",
                         f"Received {message_data} with exception {e1}.")
    message.ack()

# SubscriberClient() must be used in a `with` block or have __enter__() called before use.
with SubscriberClient() as subscriber_client1 , SubscriberClient() as subscriber_client2:

    streaming_pull_future = subscriber_client1.subscribe(
        subscription_path,
        callback=callback,
        per_partition_flow_control_settings=per_partition_flow_control_settings,
    )

    print(f"Listening for messages on {str(subscription_path)}...")

    utils.write_logs("info",
                      f"Listening for messages on {str(subscription_path)}...")

    streaming_power_pull_future = subscriber_client2.subscribe(
        subscription_path_allocate_power,
        callback=callback_allocate_power,
        per_partition_flow_control_settings=per_partition_flow_control_settings,
    )

    print(f"Listening for messages on {str(subscription_path_allocate_power)}...")

    utils.write_logs("info",
                     f"Listening for messages on {str(subscription_path_allocate_power)}...")

    try:
        streaming_pull_future.result()
        streaming_power_pull_future.result()
    except TimeoutError or KeyboardInterrupt:
        streaming_pull_future.cancel()
        streaming_power_pull_future.cancel()
        assert streaming_pull_future.done()
        assert streaming_power_pull_future.done()


