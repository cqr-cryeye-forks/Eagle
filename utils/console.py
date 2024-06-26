import argparse
import datetime
import re
import sys
from threading import Lock

from .status import *

lock = Lock()

banner_str = "BANNER BE HERE\n"
# statup_time = datetime.datetime.now().strftime("%d-%m-%Y.%H.%M.%S")
# open(sys.path[0] + "/logs/%s.log" % statup_time, "a+").write(' '.join(sys.argv) + "\n")

parser = argparse.ArgumentParser(description='[*] Project Eagle - Manual')
parser.add_argument('--workers', type=int, help='concurrent workers number default=5', default=5)
# parser.add_argument('--db', type=str, help='database file path', default=sys.path[0] + "/data.json")
parser.add_argument('--target', help='targets file', type=str)
parser.add_argument('--verbose', help='increase output verbosity', action="count", default=3)
parser.add_argument('--ping', action='store_true', help='check availability of targets')
parser.add_argument('--output', help='output file, save ressult by ur targets in json format. Example=data.json')
args = parser.parse_args()
if len(sys.argv) < 2:
    parser.print_help()
    exit(0)


def escape_ansi(line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


def banner(plugins):
    print(banner_str % (plugins, args.workers))


def output(level, msg):
    with lock:
        level = '{color} {name}{reset}'.format(
            color=s2c[level],
            name=s2s[level].upper(),
            reset=Fore.RESET
        ).ljust(19, " ")

        msg = "[%s] |%s| %s\n" % (datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), level, msg)

        # open(sys.path[0] + "/logs/%s.log" % statup_time, "a+").write(escape_ansi(msg))
        print(msg, end='')


def pprint(result):
    res = result.ret
    host = result.args[0]
    name = result.channel.name

    if not res: return
    if name == 'ping':
        output(res.status, "%s" % (res.msg))
        return

    if args.verbose == 0 and res.status == SUCCESS:
        output(SUCCESS, "plugin=%s, host=%s, msg=%s" % (
            name,
            host,
            res.msg
        ))

    if args.verbose == 1 and (res.status == SUCCESS or res.status == WARNING):
        output(res.status, "plugin=%s, host=%s, msg=%s" % (
            name,
            host,
            res.msg
        ))

    if args.verbose == 2 and (res.status == SUCCESS or res.status == WARNING or res.status == ERROR):
        output(res.status, "plugin=%s, host=%s, msg=%s" % (
            name,
            host,
            res.msg
        ))

    if args.verbose == 3:
        output(res.status, "plugin=%s, host=%s, status=%s, msg=%s" % (
            name,
            host,
            s2s[res.status],
            res.msg
        ))
