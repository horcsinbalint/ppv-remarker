NUMBER_OF_SWITCHES = 1
NUMBER_OF_HOSTS = 4

p4_source_per_switch = {
    "s1": "switch_program.p4"
}

links = [
    ("s1", "h1"),
    ("s1", "h2"),
    ("s1", "h3"),
    ("s1", "h4")
]

next_hop = {
    "s1" : {
        "h1": 1,
        "h2": 2,
        "h3": 3,
        "h4": 4
    }
}

marker = [
    ("s1", "10.0.0.1/32"),
    ("s1", "10.0.0.2/32")
]

demarker = [
    ("s1", "10.0.0.3/32"),
    ("s1", "10.0.0.4/32")
]


def switches() -> list[str]:
    """Return a list of switch names based on NUMBER_OF_SWITCHES."""
    return [f's{switch}' for switch in range(1, NUMBER_OF_SWITCHES+1)]

def get_ip_for_host(name: str) -> str:
    """Return the IP address for a given host name (e.g., 'h1' -> '10.0.0.1')."""
    return f"10.0.0.{name.replace('h','')}"

def get_mac_for_host(name: str) -> str:
    """Return the MAC address for a given host name (e.g., 'h1' -> '00:00:0a:00:00:01')."""
    num = int(name.replace('h',''))
    return f"00:00:0a:00:00:{num:02x}"

def check_node(host_name: str) -> None:
    """Assert that the given name is a valid switch or host name."""
    assert(host_name in [f"s{i}" for i in range(1,NUMBER_OF_SWITCHES+1)] or
           host_name in [f"h{i}" for i in range(1,NUMBER_OF_HOSTS+1)])
def check_switch(host_name: str) -> None:
    """Assert that the given name is a valid switch name."""
    assert(host_name in [f"s{i}" for i in range(1,NUMBER_OF_SWITCHES+1)])

def check() -> None:
    """Validates the configuration for switches, links, markers, and demarkers."""
    assert(NUMBER_OF_SWITCHES == len(p4_source_per_switch))
    for i in range(1, NUMBER_OF_SWITCHES+1):
        assert(f's{i}' in p4_source_per_switch)
    for (a, b) in links:
        check_node(a)
        check_node(b)
    for (a, _) in marker:
        check_switch(a)
    for (a, _) in demarker:
        check_switch(a)
