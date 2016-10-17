from marvinbot.utils import get_message
from marvinbot.handlers import CommandHandler
from marvinbot_ripe_atlas_plugin import get_config
import logging
import json
import requests
import arrow

log = logging.getLogger(__name__)
adapter = None


def fetch_probe(probe_id, api_key):
    base_url = 'https://atlas.ripe.net//api/v2/probes/{probe_id}/?key={api_key}'
    response = requests.get(base_url.format(probe_id=probe_id, api_key=api_key))
    data = response.json()
    return data


def on_probe_command(update, *args, **kwargs):
    log.info('Probe command caught')
    message = get_message(update)
    probes = kwargs.get('probe_id')
    api_key = get_config().get("api_key")
    responses = []
    for probe_id in probes:
        data = fetch_probe(probe_id, api_key)
        log.info(json.dumps(data, indent=4, sort_keys=True))
        if data.get("status") is None:
            continue
        status = data.get("status")
        values = {
            "since": arrow.get(status.get("since")).humanize(),
            "icon": "✅" if status.get("name") == "Connected" else "🅾",
            "desc": data.get("description"),
            "status_name": status.get("name")
        }
        response = "{icon} {desc}: {status_name} since {since}".format(**values)
        responses.append(response)

    if len(responses) > 0:
        adapter.bot.sendMessage(chat_id=message.chat_id,
                                text="\n".join(responses),
                                parse_mode="Markdown")


def setup(new_adapter):
    global adapter
    adapter = new_adapter

    adapter.add_handler(CommandHandler('probe', on_probe_command, command_description='Allows the user to get status for a given probe.')
                        .add_argument('probe_id', nargs='*', help='Probe ID'))
