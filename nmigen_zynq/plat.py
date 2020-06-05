from nmigen.vendor.xilinx_ultrascale import *


class ZynqMPPlatform(XilinxUltraScalePlatform):
    file_templates = {
        **XilinxUltraScalePlatform.file_templates,
        "{{name}}.bif": r"""
            all:
            {
            	[destination_device = pl] {{name}}.bit
            }
        """
    }

    command_templates = [
        *XilinxUltraScalePlatform.command_templates,
        r"""
            bootgen
            -image {{name}}.bif
            -arch zynqmp
            -w
            -o {{name}}_bootgen.bin
        """
    ]


