import os
import sys
import json
import csv
import time
import asyncio
import socket
from contextlib import closing

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.modularinput import *

class Input(Script):
    MASK = "<encrypted>"
    APP = "TA-tcpcheck"

    def get_scheme(self):

        scheme = Scheme("TCP Port Check")
        scheme.description = ("A high performance TCP Port Checker input")
        scheme.use_external_validation = False
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False

        scheme.add_argument(Argument(
            name="file",
            title="Host List File",
            data_type=Argument.data_type_string,
            required_on_create=True,
            required_on_edit=False
        ))
        scheme.add_argument(Argument(
            name="concurrency",
            title="Concurrency Limit",
            data_type=Argument.data_type_number,
            required_on_create=True,
            required_on_edit=False
        ))
        scheme.add_argument(Argument(
            name="timeout",
            title="Timeout",
            data_type=Argument.data_type_number,
            required_on_create=True,
            required_on_edit=False
        ))
        return scheme

    def stream_events(self, inputs, ew):
        self.service.namespace['app'] = self.APP
        # Get Variables
        input_name, input_items = inputs.inputs.popitem()
        kind, name = input_name.split("://")
        CONCURRENCY = int(input_items['concurrency'])
        TIMEOUT = int(input_items['timeout'])

        # Format Target List
        targets = []
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..",input_items['file']), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for target in reader:
                if target.get('enabled') == "1":
                    targets.append([target['target'],int(target['port']),target['asset']])

        ew.log(EventWriter.INFO,f"Connecting to {len(targets)} targets with a concurrency of {CONCURRENCY} and timeout of {TIMEOUT}")
        start = time.perf_counter()

        asyncio.run(self.tcp_multi(targets, TIMEOUT, CONCURRENCY, ew, input_items['sourcetype']))
        
        stop = time.perf_counter()
        ew.log(EventWriter.INFO,f"Completed in {format(stop-start,'.3f')}s")

    async def tcp_multi(self, targets, timeout, concurrent_tasks, ew, sourcetype):
        loop = asyncio.get_running_loop()
        tasks_pending = set()

        for [address,port,asset] in targets:
            if len(tasks_pending) >= concurrent_tasks:
                _, tasks_pending = await asyncio.wait(tasks_pending,return_when=asyncio.FIRST_COMPLETED)

            task = loop.create_task(self.tcp_print(address, port, asset, timeout, ew, sourcetype))
            tasks_pending.add(task)

        await asyncio.wait(tasks_pending)

    async def tcp_print(self, address, port, asset, timeout, ew, sourcetype):
        data = None
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.settimeout(timeout)
                error = sock.connect_ex((address, port))
        except OSError as e:
            ew.log(EventWriter.ERROR,f"TA-tcpcheck address=\"{address}:{port}\" asset=\"{asset}\" error=\"{e.__class__.__name__}\" message=\"{e}\"")
            error = -1
        except Exception as e:
            ew.log(EventWriter.ERROR,f"TA-tcpcheck address=\"{address}:{port}\" asset=\"{asset}\" error=\"{e.__class__.__name__}\" message=\"{e}\"")
            error = -2
        if data:
            ew.write_event(Event(
                data=f"{asset}|{error}",
                source=f"{address}:{port}",
            ))

if __name__ == '__main__':
    exitcode = Input().run(sys.argv)
    sys.exit(exitcode)