from amaranth import *
from amaranth.lib.cdc import ResetSynchronizer
from amaranth_zynq.ps8.ps import PsZynqMP
from amaranth_zynq.ps8.plat import ZynqMPPlatform
from amaranth_wb2axip import Axi2AxiLite, AxiLiteXBar, DemoAxi, AxiMaster
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
        axi_master = AxiMaster.from_record(axi_ps)

        axi2axil = Axi2AxiLite(data_w=32, addr_w=16, id_w=5, domain='sync')
        m.submodules.axi2axil = axi2axil
        m.d.comb += axi_master.connect(axi2axil.axi)

        xbar = AxiLiteXBar(data_w=32, addr_w=16, domain='sync')
        m.submodules.xbar = xbar
        xbar.add_master(axi2axil.axilite)

        for i in range(5):
            demo = DemoAxi(32, 16, 'sync')
            m.submodules['demo' + str(i)] = demo
            xbar.add_slave(demo.axilite, 0x1000 * i, 0x1000)

        return m


core = AxiExample()
plat = Zu3egPlatform()
plat.build(core)
