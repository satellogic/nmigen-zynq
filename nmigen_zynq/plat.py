from amaranth.vendor.xilinx_ultrascale import *


class ZynqMPPlatform(XilinxUltraScalePlatform):
    _vivado_file_templates = {
        **XilinxUltraScalePlatform._vivado_file_templates,
        "{{name}}.bif": r"""
            all:
            {
            	[destination_device = pl] {{name}}.bit
            }
        """
    }

    _vivado_command_templates = [
        *XilinxUltraScalePlatform._vivado_command_templates,
        r"""
            bootgen
            -image {{name}}.bif
            -arch zynqmp
            -w
            -o {{name}}_bootgen.bin
        """
    ]


