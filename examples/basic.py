from amaranth import *
from amaranth.lib.cdc import ResetSynchronizer
from amaranth_zynq.ps8.ps import PsZynqMP
from amaranth_zynq.ps8.plat import ZynqMPPlatform


class Zu3egPlatform(ZynqMPPlatform):
    device     = 'xczu3eg'
    package    = 'sfva625'
    speed      = '1'
    grade      = 'e'
    resources  = []
    connectors = []


class BasicExample(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        m.domains += ClockDomain('sync')
        m.submodules.ps = ps = PsZynqMP()

        cnt = Signal(29)
        m.d.sync += cnt.eq(cnt + 1)
        m.d.comb += ps.get_irq_signal(0).eq(cnt[-1])

        clk = ps.get_clock_signal(0, 200e6)
        m.d.comb += ClockSignal('sync').eq(clk)

        reset = ps.get_reset_signal(0)
        reset_sync = ResetSynchronizer(reset, domain='sync')
        m.submodules.reset_sync = reset_sync
        return m


core = BasicExample()
plat = Zu3egPlatform()
plat.build(core)
