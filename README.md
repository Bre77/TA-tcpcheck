A high performance TCP Port Check input that uses python sockets. Designed for high volume concurrent testing, and utilizes a CSV file for targets.

Data written with minimal raw size (license usage), and utilizes indexed extractions for maximum performance with tstats.

https://splunkbase.splunk.com/app/6455/

# Configuration
Create an inputs.conf that includes:

```
**file** = file path relative to the app that contains a CSV file with the headings target,port,asset,enabled
**concurrency** = How many sockets to try open at once
**timeout** = How long to wait for each socket to open
**interval** = How often to check all the targets
```

For example, the defaults are:
```
file = default/targets.csv
concurrency = 50
timeout = 2
interval = 300
```

# Targets CSV file
- **target** should be an IP address for best performance, to avoid doing repetitive DNS queries on every check.
- **port** must be a valid TCP port between 1 and 65535.
- **asset** is a free text field that alows you to add a human readable label for the thing your checking. This is where you would put the host name or similar.
- **enabled** allows you to disable an entry without removing it from the list.