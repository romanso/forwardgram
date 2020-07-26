from telethon import TelegramClient, events, sync, tl
from telethon.tl.types import InputChannel
import yaml
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


def start(config):
    client = TelegramClient(config["session_name"],
                            config["api_id"],
                            config["api_hash"])
    client.start()

    print(config)

    input_channels_entities = []
    output_channel_entities = []
    for d in client.iter_dialogs():

        if d.name in config["input_channel_names"] or \
           d.entity.id in config["input_channel_ids"]:
            print(d.name, d.entity.id, type(d.entity))
            input_channels_entities.append(InputChannel(d.entity.id, d.entity.access_hash))
        if d.name in config["output_channel_names"] or \
           d.entity.id in config["output_channel_ids"]:
            print(d.name, type(d.entity))
            output_channel_entities.append(InputChannel(d.entity.id, d.entity.access_hash))
        if d.name in config["output_chat_names"] or \
           d.entity.id in config["output_chat_ids"]:
            print(d.name, type(d.entity))
            assert isinstance(d.entity, tl.types.Chat)
            output_channel_entities.append(d.entity.id)

    if not output_channel_entities:
        logger.error(f"Could not find any output channels in the user's dialogs")
        sys.exit(1)

    if not input_channels_entities:
        logger.error(f"Could not find any input channels in the user's dialogs")
        sys.exit(1)

    logging.info(f"Listening on {len(input_channels_entities)} channels. Forwarding messages to {len(output_channel_entities)} channels.")

    @client.on(events.NewMessage(chats=input_channels_entities))
    async def handler(event):
        for output_channel in output_channel_entities:
            await client.forward_messages(output_channel, event.message)

    client.run_until_disconnected()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} {{CONFIG_PATH}}")
        sys.exit(1)
    with open(sys.argv[1], 'rb') as f:
        config = yaml.safe_load(f)
    start(config)
