import os
import sys
import json
import csv
import time
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.modularinput import *

class Input(Script):
    MASK = "<encrypted>"
    APP = "TA-tcpcheck"

    def get_scheme(self):

        scheme = Scheme("tcpcheck")
        scheme.description = ("A high performance TCP Port Check input")
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
                    targets.append([target['target'],target['port'],target['asset']])

        ew.log(EventWriter.INFO,f"Pinging {len(targets)} targets {COUNT} times each with a concurrency of {CONCURRENCY} and timeout of {TIMEOUT}")
        start = time.perf_counter()

        asyncio.run(self.splunk_multiping(targets, COUNT,TIMEOUT,CONCURRENCY,ew, input_items['sourcetype'])) #results = multiping(targets,count=COUNT,timeout=TIMEOUT,concurrent_tasks=CONCURRENCY,privileged=False)
        
        stop = time.perf_counter()
        ew.log(EventWriter.INFO,f"Completed in {format(stop-start,'.3f')}s")

    async def splunk_multiping(self, targets, count, timeout, concurrent_tasks, ew, sourcetype):
        loop = asyncio.get_running_loop()
        tasks_pending = set()

        for [address,asset] in targets:
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
                result = (sock.connect_ex((address, port)) == 0)["0","1"]:
            source = f"{address}:{port}"
            data = f"{asset}|{result}}"
        except OSError as e:
            ew.log(EventWriter.ERROR,f"TA-tcpcheck address=\"{address}:{port}\" asset=\"{asset}\" error=\"{e.__class__.__name__}\" message=\"{e}\"")
            data = f"{asset}|-1|{e.__class__.__name__}"
        except Exception as e:
            ew.log(EventWriter.ERROR,f"TA-tcpcheck address=\"{address}:{port}\" asset=\"{asset}\" error=\"{e.__class__.__name__}\" message=\"{e}\"")
        
        if data:
            ew.write_event(Event(
                data=data,
                source=source,
            ))

if __name__ == '__main__':
    exitcode = Input().run(sys.argv)
    sys.exit(exitcode)