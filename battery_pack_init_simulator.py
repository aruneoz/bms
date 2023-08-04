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
  "type": "service_account",
  "project_id": "greenfielddemos",
  "private_key_id": "4c6fe59343f2e6aa131891e5d1196684ea9fa953",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCN1dNzUzlDNFlK\nrB1662qJuFdod0ILCLpTWLc4jvAJ7L0rNgBjcA3xZpQe1m/mRbxkJPGJgLR7W19W\ny0Zec6+/qRJcRl0+M2U+nki0/g75DC7tosXkKo8Z5VH0k0eAZPdVv4USnP9FGp/H\nZZKL8L6D0dWXsl0oPYeS8sPeLVPpsuATVEubq/K1at0UM59W0VWBDliwowFyayP4\nlO0RB6gCjsjqZI9qQiGRab9QnvYWdJlFFAjvMxjoqoHNS/L8scvhIHMV7dpSzbgq\n+Tvv4V91D+/DwEa6+2Bqji30Hj/OBeY4o1br5ZfAmVazkJhA4rPAYe3QIW36+VhK\nwAN5hMNLAgMBAAECggEAE2niIGs9b5fEZQvRQ9g3OT80ekW153a8B4PMHaoK7FYt\nal22Mzt3h8Q89UpFVLp/gnbqt0xuPQ2RANCgAsuePFidp72wg5QGAUp/CdmrHlGZ\nlsiXLOzaW3a0/19YA8NOILwvMGYG1rmXMcloWU6MH9Tigc9Vyu0+bPxc7Os9Yhj3\n56ZWLiuZOuwJ8okbHPsorMwrgrvNDv9SahS261S8TVa01dxGtlb/d0NF9OUQn1Go\noA4POF8NCm1D7aai92aFybs69heoKEksbUCh17MZO41utMmCxrf/PxdC8HnzaIEF\n5y4ybUKuVBlIKCtjgcT+BeB6exncQC2wcsPQtA3nAQKBgQDEOq9o1ruj/1wCstyo\n2xL8vR46tSa+DXVXnOHFYrdo8PItpZBUbgsVwsDT/tWn0Hza2RuFmwfXWbAtSC1P\nBp/fr0RTAnLz5oq2s0OkEVewQzILPOlze5cgNyhMs2Z5iIunykFl+SxNxZdidOJt\nP4zG9rC1SnSHZ/so7cySCVOwywKBgQC5Ca0GLj4cbjMq0sw81A2PeZcMk52GrMfe\nOKkNZ7gSCGwOuqIBW5436S34EkcspNwcUle4Gm2FMM+gW9Y9WswJM6D0ZygJQEPS\nkRGjAkUNGLIiwOFb3U07D7NonlPMQGKmYbVolmrqOJX534ICVVRLb1DE+OKZohxL\nVj8TasVngQKBgHfiPp43aoYEEcuYSNVkmlIMnHZTjCragBEZyJlV+SXE5sBagTYD\n0QPnavVZoGCZMF5n+7eBgqXfppHTodLBAlWfd4ebXG2EMMTz+mQ3MDKAqwdQnHOw\nUyEccaOCix2+/Utydsf9FkMhb554OIl0JOa9ejIYHd9H+JsFxVCHIDlHAoGBAIJl\ndzEr1Uljv1smQhd7uDKrlO6f+Bq4GAFaHIf915GdrciTbSdX0R/Fi0eOWen0I8kx\nne93cEa0Jxzymv+RxMeXQo35RBWA3Eq/QJaHOvIHvUEQe7+pLIu6fMv1B0ig9uQZ\nZyXVGnMEfWwhPhU23LhsMZcdbVKnExlkJf8g9wwBAoGBALyFmIntr3EDtAKJLMhG\nk22LCw+WIRFHT+x0DOjIc0+kJ5i0s9LPCiwdphAUtunOSj9VuiPhpZbHt+OTrdaw\nA5uL9D+b1n3IYBz5t92axFMFGRfDLk3GK3E2LToHF5/6I/Fv1F1eqUJkQFQOHDsl\nz5moTAiI9Xk2m8+5243jQYtu\n-----END PRIVATE KEY-----\n",
  "client_email": "bms-svc-acct@greenfielddemos.iam.gserviceaccount.com",
  "client_id": "109213598062139450151",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bms-svc-acct%40greenfielddemos.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
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

