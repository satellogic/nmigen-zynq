from nmigen import Elaboratable, Signal, Module, Instance
from .layouts import get_ps8_layout


class PsSignal(Signal):
    def __init__(self, *argc, dir=None, **argv):
        Signal.__init__(self, *argc, **argv)
        self.dir = dir

class PsZynqMP(Elaboratable):
    MAXI = ['maxigp0', 'maxigp1', 'maxigp2']
    SAXI = [
        'saxigp0', 'saxigp1', 'saxigp2', 'saxigp3',
        'saxigp4', 'saxigp5', 'saxigp6', 'saxiacp',
    ]
    CLK = 'PLCLK'
    IRQ = ['PLPSIRQ0', 'PLPSIRQ1']

    def __init__(self):
        ps_layout = get_ps8_layout()
        self._ports = self.get_ps_ports(ps_layout)
        self._clocks = [None for _ in range(4)]

    def get_ps_ports(self, layout):
        return {p: PsSignal(w, name=p.lower(), dir=d) for p,w,d in layout}

    def get_clock_signal(self, n, freq):
        assert n < 4
        assert self._clocks[n] is None, (
            'Clock already taken')
        clk = Signal(name='pl_clk{}'.format(n))
        self._clocks[n] = (clk, freq)
        return clk

    def get_irq_signal(self, n):
        assert n < 16
        return self._ports[self.IRQ[n // 8]][n % 8]

    def get_reset_signal(self, n):
        assert n < 4
        return ~self._ports['EMIOGPIOO'][-1 - n]

    def _get_ports(self):
        ports = {}
        for p, s in self._ports.items():
            if s.dir == 'input':
                prefix = 'i_'
            elif s.dir == 'output':
                prefix = 'o_'
            else:
                prefix = 'o_'
            ports[prefix + p] = s
        return ports

    def elaborate(self, platform):
        m = Module()
        for i, val in enumerate(self._clocks):
            if val is not None:
                clk, freq = val
                unbuf = Signal(name='pl_clk{}_unbuf'.format(i))
                platform.add_clock_constraint(unbuf, freq)

                m.d.comb += unbuf.eq(self._ports[self.CLK][i])
                buf = Instance(
                    'BUFG_PS',
                     i_I=unbuf,
                     o_O=clk
                );
                m.submodules['clk{}_buffer'.format(i)] = buf

        ps_i = Instance(
            'PS8',
            a_DONT_TOUCH="true",
            **self._get_ports(),
        )

        m.submodules.ps_i = ps_i
        return m
