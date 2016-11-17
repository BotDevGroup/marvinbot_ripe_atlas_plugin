from marvinbot.utils import get_message, localized_date
from marvinbot.handlers import CommandHandler
from marvinbot_ripe_atlas_plugin.models import ProbeAlias
from marvinbot_ripe_atlas_plugin import get_config
import logging
import json
import requests
import arrow

log = logging.getLogger(__name__)
adapter = None


def remove_probe_alias(alias):
    probe_alias = ProbeAlias.by_alias(alias)
    if probe_alias and probe_alias.date_deleted is None:
        probe_alias.date_deleted = localized_date()
        try:
            probe_alias.save()
            return True
        except:
            return False
    return False


def query_probe_status(probe_id, api_key):
    base_url = 'https://atlas.ripe.net//api/v2/probes/{probe_id}/?key={api_key}'
    try:
        response = requests.get(base_url.format(probe_id=probe_id, api_key=api_key))
        if response.ok:
            data = response.json()
            return data
        else:
            return None
    except:
        return None


def on_probe_alias_command(update, *args, **kwargs):
    log.info('on_probe_alias_command')
    message = get_message(update)
    probe_id = kwargs.get('probe_id')
    alias = kwargs.get('alias')
    remove = kwargs.get('remove')

    if alias is None:
        adapter.bot.sendMessage(chat_id=message.chat_id,
                                text="❌ You must specify an alias.")
        return

    if len(alias) == 0:
        adapter.bot.sendMessage(chat_id=message.chat_id,
                                text="❌ Specified alias is too short")
        return

    if remove:
        if remove_probe_alias(alias):
            adapter.bot.sendMessage(chat_id=message.chat_id,
                                    text="🚮 1 probe alias removed.")
        else:
            adapter.bot.sendMessage(chat_id=message.chat_id,
                                    text="❌ No such probe alias.")
        return

    if probe_id is None:
        adapter.bot.sendMessage(chat_id=message.chat_id,
                                text="❌ You must specify a probe.")
        return

    if len(probe_id) == 0:
        adapter.bot.sendMessage(chat_id=message.chat_id,
                                text="❌ Specified probe ID is too short.")
        return

    probe_alias = ProbeAlias.by_alias(alias)

    if probe_alias:
        if probe_alias.date_deleted is None:
            adapter.bot.sendMessage(chat_id=message.chat_id,
                                    text="❌ Probe alias already exists.")
            return

    user_id = message.from_user.id
    username = message.from_user.username
    date_added = localized_date()
    date_modified = localized_date()

    if probe_alias is None:
        probe_alias = ProbeAlias()

    probe_alias.probe_id = probe_id
    probe_alias.alias = alias
    probe_alias.user_id = user_id
    probe_alias.username = username
    probe_alias.date_modified = date_modified
    probe_alias.date_deleted = None

    try:
        probe_alias.save()
        adapter.bot.sendMessage(chat_id=message.chat_id, text="✅ Probe alias added.")
    except:
        adapter.bot.sendMessage(chat_id=message.chat_id,
                                text="❌ Unable to add probe alias.")


def on_probe_command(update, *args, **kwargs):
    message = get_message(update)
    probes = kwargs.get('probe_id')
    api_key = get_config().get("api_key")
    responses = []
    for probe in probes:
        if probe.isdigit():
            probe_id = probe
        else:
            probe_alias = ProbeAlias.by_alias(probe)
            if probe_alias is None or probe_alias.date_deleted is not None:
                adapter.bot.sendMessage(chat_id=message.chat_id,
                                        text="❌ Not a valid probe alias.")
                return
            else:
                probe_id = probe_alias.probe_id
        data = query_probe_status(probe_id, api_key)
        if not data:
            adapter.bot.sendMessage(chat_id=message.chat_id,
                                    text="❌ Probe does not exist.")
            continue
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
    adapter.add_handler(CommandHandler('probe_alias', on_probe_alias_command, command_description='Allows the user to set an alias for a given probe.')
                        .add_argument('--remove', help='Remove alias', action='store_true')
                        .add_argument('--alias', help='Set an alias (e.g. Santiago)')
                        .add_argument('--probe_id', help='Probe ID (e.g. 11816)'))
