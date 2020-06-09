from nmigen import *
from nmigen.lib.cdc import ResetSynchronizer
from nmigen_zynq.ps import PsZynqMP
from nmigen_zynq.plat import ZynqMPPlatform
from nmigen_zynq.layouts import get_axi_layout
from urllib import request




class Zu3egPlatform(ZynqMPPlatform):
    device     = 'xczu3eg'
    package    = 'sfva625'
    speed      = '1'
    grade      = 'e'
    resources  = []
    connectors = []


def get_axilite_layout(data_w, addr_w):
    return [
		('AWADDR', addr_w, 'input'),
		('AWPROT', 3, 'input'),
		('AWVALID', 1, 'input'),
		('AWREADY', 1, 'output'),
		('WDATA', data_w, 'input'),
		('WSTRB', data_w // 8, 'input'),
		('WVALID', 1, 'input'),
		('WREADY', 1, 'output'),
		('BRESP', 2, 'output'),
		('BVALID', 1, 'output'),
		('BREADY', 1, 'input'),
		('ARADDR', addr_w, 'input'),
		('ARPROT', 3, 'input'),
		('ARVALID', 1, 'input'),
		('ARREADY', 1, 'output'),
		('RDATA', data_w, 'output'),
		('RRESP', 2, 'output'),
		('RVALID', 1, 'output'),
		('RREADY', 1, 'input'),
    ]

def prefix(dir):
    return 'i_' if dir == 'input' else 'o_'

AXI_EXCLUDE = [
    'ARUSER', 'AWUSER', 'RACOUNT',
    'RCOUNT', 'WACOUNT', 'WCOUNT',
    'WCLK', 'RCLK', 'ACLK'
]

class Axi2AxiLite(Elaboratable):
    def __init__(self, data_w, addr_w, id_w, domain='sync'):

        self.axi_layout = get_axi_layout('slave', data_w, addr_w, id_w)
        self.axil_layout = get_axilite_layout(data_w, addr_w)

        self.axi_layout = [l for l in self.axi_layout if l[0] not in AXI_EXCLUDE]

        self.axil = Record(
            [(f, w) for f, w, d in self.axil_layout],
            name='M_AXI'
        )
        self.axi = Record(
            [(f, w) for f, w, d in self.axi_layout],
            name='S_AXI'
        )
        self.data_w = data_w
        self.addr_w = addr_w
        self.id_w = id_w
        self.domain = domain

    def elaborate(self, platform):
        m = Module()
        sync = m.d[self.domain]

        axi_fields = {
            prefix(d) + 'S_AXI_' + f: self.axi[f]
            for f, w, d in self.axi_layout
        }

        axil_fields = {
            prefix('output' if d == 'input' else 'input') +
            'M_AXI_' + f: self.axil[f]
            for f, w, d in self.axil_layout
        }

        axi2axil_i = Instance(
            'axi2axilite',
            p_C_AXI_ID_WIDTH=self.id_w,
	        p_C_AXI_DATA_WIDTH=self.data_w,
	        p_C_AXI_ADDR_WIDTH=self.addr_w,
            i_S_AXI_ACLK=ClockSignal(self.domain),
            i_S_AXI_ARESETN=~ResetSignal(self.domain),
            **axi_fields,
            **axil_fields,
        )

        m.submodules.axi2axil_i = axi2axil_i
        return m


class DemoAxi(Elaboratable):
    def __init__(self, data_w, addr_w, domain='sync'):
        self.layout = get_axilite_layout(data_w, addr_w)
        self.axil = Record(
            [(f, w) for f, w, d in self.layout],
            name='S_AXI'
        )
        self.data_w = data_w
        self.addr_w = addr_w
        self.domain = domain

    def elaborate(self, platform):
        m = Module()
        sync = m.d[self.domain]

        fields = {
            prefix(d) + 'S_AXI_' + f: self.axil[f]
            for f, w, d in self.layout
        }

        demo = Instance(
            'demoaxi',
	        p_C_S_AXI_DATA_WIDTH=self.data_w,
	        p_C_S_AXI_ADDR_WIDTH=self.addr_w,
            i_S_AXI_ACLK=ClockSignal(self.domain),
            i_S_AXI_ARESETN=~ResetSignal(self.domain),
            **fields
        )

        m.submodules.demo_i = demo
        return m

class AxiExample(Elaboratable):
    def connect_axi(self, master, slave):
        layout = [
            (f, d) for f, _, d in get_axi_layout('master')
            if f not in AXI_EXCLUDE
        ]
        ret = [master[f].eq(slave[f]) for f, d in layout if d == 'input']
        ret += [slave[f].eq(master[f]) for f, d in layout if d == 'output']
        return ret

    def connect_axi_lite(self, master, slave):
        layout = [(f, d) for f, _, d in get_axilite_layout(0, 0)]
        ret = [master[f].eq(slave[f]) for f, d in layout if d == 'output']
        ret += [slave[f].eq(master[f]) for f, d in layout if d == 'input']
        return ret

    def elaborate(self, platform):
        m = Module()
        m.domains += ClockDomain('sync')
        m.submodules.ps = ps = PsZynqMP()

        clk = ps.get_clock_signal(0, 200e6)
        m.d.comb += ClockSignal().eq(clk)
        reset = ps.get_reset_signal(0)
        reset_sync = ResetSynchronizer(reset, domain="sync")
        m.submodules.reset_sync = reset_sync

        axi_ps = ps.get_axi('maxigp2')
        m.d.comb += axi_ps['ACLK'].eq(clk)

        axi2axil = Axi2AxiLite(data_w=32, addr_w=8, id_w=5, domain='sync')
        m.submodules.axi2axil = axi2axil
        m.submodules.demo = demo = DemoAxi(32, 8, 'sync')

        m.d.comb += self.connect_axi(axi_ps, axi2axil.axi)
        m.d.comb += self.connect_axi_lite(axi2axil.axil, demo.axil)
        return m


url_path = 'https://raw.githubusercontent.com/ZipCPU/wb2axip/master/rtl/{}'
dependencies = ['axi2axilite.v', 'demoaxi.v', 'skidbuffer.v', 'axi_addr.v', 'sfifo.v']

core = AxiExample()
plat = Zu3egPlatform()
for d in dependencies:
    url = url_path.format(d)
    print('Downloading ' + d)
    content = request.urlopen(url).read()
    plat.add_file(d, content)
plat.build(core)

