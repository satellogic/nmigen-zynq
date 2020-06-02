import re
import argparse


def to_width(s):
    if s == '':
        s = '0'
    return int(s) + 1


class PsParser:
    def __init__(self, ps8):
        with open(ps8) as f:
            self.data = f.read()
        self.ports = self.get_ports()

    def get_ports(self):
        expr = r'^ *(input|output|inout) (\[(.*):.*\] )?(\w*)'
        ports = re.findall(expr, self.data, re.MULTILINE)
        ports = {p[-1]: (to_width(p[2]), p[0]) for p in ports}
        return ports

    def generate_ps_layout(self):
        txt  = 'def get_ps8_layout():\n'
        txt += '    ports = [\n'
        for k, (w, d) in self.ports.items():
            txt += '        ("{}", {}, "{}"),\n'.format(k, w, d)
        txt += '    ]\n'
        txt += '    return ports\n'
        return txt

    def get_default_width(self, port):
        return self.ports[port][0]

    def generate_axi_layout(self):
        axis = [('MAXIGP0', 'master'), ('SAXIGP0', 'slave'), ('SAXIACP', 'slave_acp')]
        txt = 'def get_axi_layout(axi, data_w=None, addr_w=None, id_w=None):\n'
        txt += '    assert data_w is None or data_w % 8 == 0\n'
        for axi_name, axi_type in axis:
            txt += '    if axi == "{}":\n'.format(axi_type)
            var_port = [
                ('data_w', axi_name + 'WDATA'),
                ('addr_w', axi_name + 'AWADDR'),
                ('id_w', axi_name + 'AWID')
            ]
            for var, port in var_port:
                txt += '        if {} is None:\n'.format(var)
                txt += '            {} = {}\n'.format(var, self.get_default_width(port))
            txt += '        return [\n'
            for p, w, d in ps.get_interface(axi_name):
                field = p.split(axi_name)[1]
                if 'DATA' in field:
                    w = 'data_w'
                if 'ADDR' in field:
                    w = 'addr_w'
                if 'STRB' in field:
                    w = 'data_w // 8'
                if 'ID' in field and 'VALID' not in field:
                    w = 'id_w'
                txt += '            ("{}", {}, "{}"),\n'.format(field, w, d)
            txt += '        ]\n'
        txt += '    raise ValueError("Invalid axi interface")\n'
        return txt

    def get_interface(self, name):
        return [(p, w, d) for p, (w, d) in self.ports.items() if p.startswith(name)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help='PS8.v unisim file')
    parser.add_argument('-o', default=None, help='output file')
    args = parser.parse_args()
    ps = PsParser(args.i)

    layout_file = ps.generate_ps_layout()
    layout_file += '\n\n'
    layout_file += ps.generate_axi_layout()

    if args.o:
        with open(args.o, 'w') as f:
            f.write(layout_file)
    else:
        print(layout_file)
