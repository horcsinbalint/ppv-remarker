import sys

try:
    from p4utils.mininetlib.network_API import NetworkAPI
except ImportError as e:
    print("[ERROR] Could not import p4utils.mininetlib.network_API.\n"
          "Make sure you are running this code in the p4-utils VM or have p4utils installed.\n"
          "See the 'Environment' section in the README for setup instructions: https://github.com/nsg-ethz/p4-utils\n"
          f"Original error: {e}", file=sys.stderr)
    sys.exit(1)
import configuration as conf

conf.check()

net = NetworkAPI()

net.setLogLevel('info')
net.setCompiler(p4rt=True)

for switch in conf.p4_source_per_switch:
    net.addP4RuntimeSwitch(switch)
    net.setP4Source(switch, conf.p4_source_per_switch[switch])
for host in range(1, conf.NUMBER_OF_HOSTS+1):
    net.addHost(f'h{host}')

for (a,b) in conf.links:
    net.addLink(a, b, params={'bw': 1})

net.l2()

net.disablePcapDumpAll()
net.disableLogAll()
net.enableCli()
net.startNetwork()