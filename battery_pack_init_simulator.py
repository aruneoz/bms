import json
import traceback

from google.cloud.pubsublite.cloudpubsub import PublisherClient, SubscriberClient
from google.cloud.pubsublite.types import (
    CloudRegion,
    CloudZone,
    MessageMetadata,
    TopicPath, SubscriptionPath, FlowControlSettings,
)
from google.oauth2 import service_account
from google.pubsub_v1 import PubsubMessage

# TODO(developer):
project_number = 779370283097
cloud_region = "us-central1"
init_battery_topic_id = "svp.simulation.battery.initialize.req"
power_allocate_topic_id = "svp.simulation.battery.power.req"
subscription_id = "batteryStatusSub"
timeout = 90
regional = True

if regional:
    location = CloudRegion(cloud_region)

topic_path = TopicPath(project_number, location, init_battery_topic_id)

power_topic_path = TopicPath(project_number, location, power_allocate_topic_id)

# PublisherClient() must be used in a `with` block or have __enter__() called before use.
with PublisherClient() as initialize_publisher_client:
    data = '{"batteryPacks": 6}'
    api_future = initialize_publisher_client.publish(topic_path, data.encode("utf-8"))
    # result() blocks. To resolve API futures asynchronously, use add_done_callback().
    message_id = api_future.result()
    message_metadata = MessageMetadata.decode(message_id)
    print(
        f"Published a message to {topic_path} with partition {message_metadata.partition.value} and offset {message_metadata.cursor.offset}."
    )

with PublisherClient() as power_publisher_client:
    data = '{"power": 10}'
    api_future = power_publisher_client.publish(power_topic_path, data.encode("utf-8"))
    # result() blocks. To resolve API futures asynchronously, use add_done_callback().
    message_id = api_future.result()
    message_metadata = MessageMetadata.decode(message_id)
    print(
        f"Published a message to {power_topic_path} with partition {message_metadata.partition.value} and offset {message_metadata.cursor.offset}."
    )

subscription_path = SubscriptionPath(project_number, location, subscription_id)

per_partition_flow_control_settings = FlowControlSettings(
    # 1,000 outstanding messages. Must be >0.
    messages_outstanding=1000,
    # 10 MiB. Must be greater than the allowed size of the largest message (1 MiB).
    bytes_outstanding=10 * 1024 * 1024,
)

def callback(message: PubsubMessage):
    try:
        message_data = message.data.decode("utf-8")
        metadata = MessageMetadata.decode(message.message_id)
        print(
            f"Received {message_data} of ordering key {message.ordering_key} with id {metadata}."
        )
        y = json.loads(message_data)



    except Exception:
        traceback.print_exc()

    message.ack()

gcp_sa_credentials={
# change with ur service key
}

project_id=gcp_sa_credentials["project_id"]

credentials = service_account.Credentials.from_service_account_info(gcp_sa_credentials)

# SubscriberClient() must be used in a `with` block or have __enter__() called before use.
with SubscriberClient(credentials=credentials) as subscriber_client1:

    streaming_pull_future = subscriber_client1.subscribe(
        subscription_path,
        callback=callback,
        per_partition_flow_control_settings=per_partition_flow_control_settings,
    )

    print(f"Listening for messages on {str(subscription_path)}...")


    try:
        streaming_pull_future.result(timeout)

    except TimeoutError or KeyboardInterrupt:
        streaming_pull_future.cancel()
        assert streaming_pull_future.done()

