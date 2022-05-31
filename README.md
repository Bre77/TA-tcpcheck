A high performance ICMP input that uses icmplib. Designed for high volume concurrent testing, and utilizes a CSV file for targets. Data written with minimal raw size (license usage), and utilizes indexed extractions for maximum performance with tstats.

OS configuration may be required to run without root, see https://github.com/ValentinBELYN/icmplib/blob/main/docs/6-use-icmplib-without-privileges.md

Use the sourcetype icmp:metric for metric indexes.

Helpful Tips:
When packets_sent=0 there was an issue preventing the ICMP being sent. Check the source field and _internal logs
When packets_received=0 the target is down