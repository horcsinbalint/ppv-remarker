import csv
import json
import os
import sys
import time

try:
    from p4utils.utils.helper import load_topo
    from p4utils.utils.sswitch_p4runtime_API import SimpleSwitchP4RuntimeAPI
    from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
except ImportError as e:
    print("[ERROR] Could not import p4utils modules.\n"
          "Make sure you are running this code in the p4-utils VM or have p4utils installed.\n"
          "See the 'Environment' section in the README for setup instructions: https://github.com/nsg-ethz/p4-utils\n"
          f"Original error: {e}", file=sys.stderr)
    sys.exit(1)
import configuration as conf

# This sould be automatically generated when the network is started.
topo = load_topo('topology.json')
controllers = {}
thrift_apis = {}
conf.check()
p4switches = topo.get_p4rtswitches()

for switch, data in p4switches.items():
    controllers[switch] = SimpleSwitchP4RuntimeAPI(data['device_id'], data['grpc_port'],
                                                   p4rt_path=data['p4rt_path'],
                                                   json_path=data['json_path'])
for switch in topo.get_p4switches():
    thrift_port = topo.get_thrift_port(switch)
    thrift_apis[switch] = SimpleSwitchThriftAPI(thrift_port)

for switch in conf.switches():
    controller = controllers[switch]
    for hop in conf.next_hop[switch]:
        controller.table_add('ipv4_lpm', 'ipv4_forward', [conf.get_ip_for_host(hop)],
                             [conf.get_mac_for_host(hop), str(conf.next_hop[switch][hop])])

for (switch, ip) in conf.marker:
    controller = controllers[switch]
    controller.table_add('ppv_marker', 'ppv_mark', [ip, "6"], # 6 for TCP
                            ["65535"]) # Value
    controller.table_add('ppv_marker', 'ppv_mark', [ip, "17"], # 17 for UDP
                            ["65535"]) # Value

for (switch, ip) in conf.demarker:
    controller = controllers[switch]
    controller.table_add('ppv_demarker', 'ppv_demark', [ip],
                            [])

try:
    with open("metered_switches_settings.json") as metered_switches_files:
        metered_switches = json.load(metered_switches_files)
except FileNotFoundError:
    print("[ERROR] Could not find 'metered_switches_settings.json'. Make sure this file exists in the project directory.\n"
          "You can copy it from the repository.", file=sys.stderr)
    sys.exit(1)

for switch in metered_switches:
    controller = controllers[switch]
    controller.table_add('ipv4_meter', 'm_action', ["0.0.0.0/0"],
                            [])
    controller.table_add('meter_filter', 'overloaded', ["2"], [])

controllers["s1"].table_add('ppv_remarker1', 'ppv_remark1', ["1"],
                            ["0", "0"])

controllers["s1"].table_add('ppv_remarker1', 'ppv_remark1', ["2"],
                            ["1", "1"])

controllers["s1"].table_add('ppv_remarker2', 'ppv_remark2', ["1"],
                            ["0", "0"])

controllers["s1"].table_add('ppv_remarker2', 'ppv_remark2', ["2"],
                            ["1", "1"])

for switch in metered_switches:
    controller = controllers[switch]
    cir = metered_switches[switch][0]
    pir = metered_switches[switch][1]
    cbursts = metered_switches[switch][2]
    pbursts = metered_switches[switch][3]
    controller.direct_meter_array_set_rates("my_meter", [(cir,cbursts), (pir,pbursts)])

used_bins = {
    "s1": 2
}

reg_history_file = "reg_history.csv"
if not os.path.exists(reg_history_file):
    with open(reg_history_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "new_reg"])

for switch in metered_switches:
    thrift_apis[switch].register_write('minimum_ppv_reg', 0, 0)
    for i in range(used_bins[switch]*5):
        thrift_apis[switch].register_write('future_bins', i, 0)
        thrift_apis[switch].register_write('old_bins', i, 0)

while True:
    for switch in metered_switches:
        if switch in used_bins:
            for i in range(used_bins[switch]*5):
                new_value = thrift_apis[switch].register_read('future_bins', i, False)
                thrift_apis[switch].register_write('future_bins', i, 0)
                thrift_apis[switch].register_write('old_bins', i, new_value)
        current_reg = thrift_apis[switch].register_read('minimum_ppv_reg', 0, False)
        if current_reg >= 1000:
            new_reg = current_reg-10
        if current_reg >= 100:
            new_reg = current_reg-5
        elif current_reg >= 10:
            new_reg = current_reg-1
        else:
            new_reg = 0
        with open(reg_history_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), current_reg])
        thrift_apis[switch].register_write('minimum_ppv_reg', 0, new_reg)
        sys.stdout.flush()
    time.sleep(0.01)