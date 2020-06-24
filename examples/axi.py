from nmigen import *
from nmigen.lib.cdc import ResetSynchronizer
from nmigen_zynq.ps import PsZynqMP
from nmigen_zynq.plat import ZynqMPPlatform
from nmigen_wb2axip import Axi2AxiLite, DemoAxi, AxiMaster
from urllib import request


class Zu3egPlatform(ZynqMPPlatform):
    device     = 'xczu3eg'
    package    = 'sfva625'
    speed      = '1'
    grade      = 'e'
    resources  = []
    connectors = []


class AxiExample(Elaboratable):
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

        axi_master = AxiMaster.from_record(axi_ps)
        m.d.comb += axi_master.connect(axi2axil.axi)
        m.d.comb += axi2axil.axilite.connect(demo.axilite)
        return m


core = AxiExample()
plat = Zu3egPlatform()
plat.build(core)

