import json
import os
import pathlib
import sys
import time
from typing import Final

from utils.db import JsonDB
from utils.status import *
import utils.multitask as multitask
import utils.console as console
import utils.data as data
import plugins
import scripts
import signal


def onexit(sig, frame):
    for plugin in plugins.loader.loaded:
        try:
            channels[plugin].close()
        except:
            pass
    # exit(0)


def dbsave(result):
    res = result.ret
    host = result.args[0]
    name = result.channel.name
    if result.ret == None: return

    console.pprint(result)

    data1 = {
        "name": name,
        "host": {
            'status': res.status,
            'msg': res.msg,
            'response': data.compress(res.response),
            'request': data.compress(res.request)

        }
    }

    data2.append(data1)

    db.save()


def scan(host):
    for plugin in plugins.loader.loaded:
        if not plugin.enable or not plugin.presquites(host):
            continue
        channels[plugin].append(host)


if __name__ == '__main__':
    output: str = console.args.output
    target: str = console.args.target
    targets = [target]

    MAIN_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent
    json_output: Final[pathlib.Path] = MAIN_DIR / output
    data2 = []
    channels = {}
    db = JsonDB(json_output, data2)

    signal.signal(signal.SIGINT, onexit)
    console.output(LOG, "checking live targets")
    if console.args.ping:
        scripts.ping(targets, silent=False)
    else:
        scripts.ping(targets, silent=True)
    console.output(LOG, "preformed in-memory save for online targets")

    for plugin in plugins.loader.loaded:
        channel = multitask.Channel(plugin.name)
        channels.update({
            plugin: channel
        })
        multitask.workers(
            target=plugin.main,
            channel=channel,
            count=console.args.workers,
            callback=dbsave
        )

    queue = multitask.Channel('scan-queue')
    multitask.workers(target=scan, channel=queue, count=console.args.workers)

    for target in targets:
        queue.append(target)

    queue.wait()
    queue.close()

    for plugin in plugins.loader.loaded:
        channels[plugin].wait()

    for plugin in plugins.loader.loaded:
        channels[plugin].close()
