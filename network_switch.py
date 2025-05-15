from enum import Enum
from collections import namedtuple

class PortType(Enum):
    ETHERNET = "Ethernet"
    SFP = "SFP"
    QSFP = "QSFP"
    FIBER_CHANNEL = "Fiber Channel"
    WIRELESS = "Wireless"
    MANAGEMENT = "Management"

# 使用 namedtuple 定義 Port
Port = namedtuple('Port', ['port_number', 'name', 'port_type', 'status', 'speed', 'sfp_model'])

# 自定義 __repr__ 方法
def port_repr(port):
    sfp_info = f", SFP Model: {port.sfp_model}" if port.port_type in [PortType.SFP, PortType.QSFP] and port.sfp_model else ""
    return f"Port {port.port_number} ({port.name}): {port.port_type.value}, {port.status}, {port.speed}{sfp_info}"

Port.__repr__ = port_repr

class Switch:
    def __init__(self, ports_info):
        self.ports = [Port(port_number, **info) for port_number, info in ports_info.items()]

    def add_port(self, port_number, name, port_type, status="down", speed="100Mbps", sfp_model=None):
        new_port = Port(port_number, name, port_type, status, speed, sfp_model)
        self.ports.append(new_port)

    def __repr__(self):
        return "\n".join(str(port) for port in self.ports)

# 定義每個埠的資訊，包括名稱、類型、狀態、速度和 SFP 型號
ports_info = {
    1: {"name": "Port A", "port_type": PortType.ETHERNET, "status": "up", "speed": "1Gbps"},
    2: {"name": "Port B", "port_type": PortType.SFP, "status": "down", "speed": "10Gbps", "sfp_model": "SFP-10G-SR"},
    3: {"name": "Port C", "port_type": PortType.QSFP, "status": "up", "speed": "40Gbps", "sfp_model": "QSFP-40G-SR4"},
    4: {"name": "Port D", "port_type": PortType.FIBER_CHANNEL, "status": "up", "speed": "8Gbps"},
    5: {"name": "Port E", "port_type": PortType.WIRELESS, "status": "up", "speed": "802.11ac"},
    6: {"name": "Port F", "port_type": PortType.MANAGEMENT, "status": "up", "speed": "100Mbps"},
    7: {"name": "Port G", "port_type": PortType.ETHERNET, "status": "up", "speed": "100Mbps"},
    8: {"name": "Port H", "port_type": PortType.SFP, "status": "down", "speed": "1Gbps", "sfp_model": "SFP-1G-LX"}
}

# 建立交換器物件
switch = Switch(ports_info)

# 新增一個埠
switch.add_port(9, "Port I", PortType.ETHERNET, "up", "1Gbps")

# 印出交換器的狀態
print(switch)
