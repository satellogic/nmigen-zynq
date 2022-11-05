from amaranth.vendor.xilinx import XilinxPlatform

__all__ = ['ZynqPL']

class ZynqPL(XilinxPlatform):
    _vivado_file_templates = None
    _vivado_command_templates = None

    def __init__(self, bif=r"{{name}}.bit"):
        self._vivado_file_templates = {
            **XilinxPlatform._vivado_file_templates,
            "{{name}}.bif": bif
        }

        self._vivado_command_templates = [
            *XilinxPlatform._vivado_command_templates,
            r"""
                bootgen
                -image {{name}}.bif
                -arch zynq
                -o BOOT.bin
                -w on
            """
        ]

        super().__init__()
