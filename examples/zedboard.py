from amaranth import *
from amaranth.lib.cdc import ResetSynchronizer
from amaranth.build import *
from amaranth_boards.resources import *
from amaranth_zynq.ps7 import ZynqPS
from amaranth_zynq.ps7 import ZynqPL

__all__ = ["ZedboardPS", "ZedboardPlatform"]

class ZedboardPS(ZynqPS):
    pass

class ZedboardPlatform(ZynqPL):
    device = "xc7z020"
    package = "clg484"
    speed = "1"
    default_clk = "GCLK"    # Use GCLK as PL clock source
    default_rst = "BTNU"    # Use BTNU as PL reset signal

    """
    Add Zedboard PL resources via following documentations:
        1. https://github.com/Avnet/hdl/blob/master/Boards/ZEDBOARD/zedboard_master_XDC_RevC_D_v2.xdc
        2. https://files.digilent.com/resources/programmable-logic/zedboard/ZedBoard_HW_UG_v2_2.pdf
    """
    resources = [
        # Audio Codec - Bank 13
        Resource("audio_i2c", 0, # ADAU1761, I2C
            Subsignal("scl", Pins("AB4", dir="io")),    # AC-SCL, I2C Clock
            Subsignal("sda", Pins("AB5", dir="io")),    # AC-SDA, I2C Data
            Subsignal("adr", Pins("AB1 Y5", dir="o")),  # AC-ADR, I2C Address Bits
            Attrs(IOSTANDARD="LVCMOS33"),
        ),
        Resource("audio_i2s", 0, # ADAU1761, I2S
            Subsignal("clk",    Pins("AA6", dir="o")),  # AC-GPIO2, Bit Clock
            Subsignal("sd_adc", Pins("AA7", dir="o")),  # AC-GPIO1, Serial-Data ADC Output
            Subsignal("sd_dac", Pins("Y8",  dir="i")),  # AC-GPIO0, Serial-Data DAC Inpupt
            Subsignal("ws",     Pins("Y6",  dir="o")),  # AC-GPIO3, Left-Right Clock
            Attrs(IOSTANDARD="LVCMOS33"),
        ),
        Resource("audio_clk", 0, # ADAU1761, MCLK
            Subsignal("mclk", Pins("AB2", dir="o")),    # AC-MCLK, Master Clock
            Attrs(IOSTANDARD="LVCMOS33"),
        ),

        # Clock Source - Bank 13, 100Mhz
        Resource("GCLK", 0, Pins("Y9", dir="i"), Clock(100e6), Attrs(IOSTANDARD="LVCMOS33")),

        # OLED Display - Bank 13
        SPIResource(0, # OLED, SSD1306, 128 x 32
            cs_n="dummy-cs0",
            clk="AB12",         # OLED-SCLK
            copi="AA12",        # OLED-DIN
            cipo="dummy-cpio0",
            reset="U9",         # OLED-RES
            attrs=Attrs(IOSTANDARD="LVCMOS33"),
        ),
        Resource("oled", 0, # OLED, UG-2832HSWEG04
            Subsignal("dc",      Pins ("U10", dir="o")),    # OLED-DC
            Subsignal("vdd_en",  PinsN("U12", dir="o")),    # OLED-VDD
            Subsignal("vbat_en", PinsN("U11", dir="o")),    # OLED-VBAT
            Attrs(IOSTANDARD="LVCMOS33"),
        ),

        # HDMI Output - Bank 33
        Resource("hdmi", 0, # ADV7511
            Subsignal("scl", Pins("AA18", dir="o")),                                                                    # HD-SCL, I2C Clock
            Subsignal("sda", Pins("Y16",  dir="io")),                                                                   # HD-SDA, I2C Data
            Subsignal("clk", Pins("W18",  dir="o")),                                                                    # HD-CLK, Video Clock
            Subsignal("vs",  Pins("W17",  dir="o")),                                                                    # HD-VSYNC, Vertical Sync
            Subsignal("hs",  Pins("V17",  dir="o")),                                                                    # HD-HSYNC, Horizontal Sync
            Subsignal("int", Pins("W16",  dir="i")),                                                                    # HD-DE, Data Enable
            Subsignal("yuv", Pins("Y13 AA12 AA14 Y14 AB15 AB16 AA16 AB17 AA17 Y15 W13 W15 V15 U17 V14 V13", dir="o")),  # HD-D[15:0], Video Data in YCbCr 4:2:2 format
            Attrs(IOSTANDARD="LVCMOS33")
        ),

        # User LEDs - Bank 33
        *LEDResources(pins={
            0: "T22",   # LD0
            1: "T21",   # LD1
            2: "U22",   # LD2
            3: "U21",   # LD3
            4: "V22",   # LD4
            5: "W22",   # LD5
            6: "U19",   # LD6
            7: "U14",   # LD7
        }, attrs=Attrs(IOSTANDARD="LVCMOS33")),

        # VGA Output - Bank 33
        VGAResource(
            0,
            r="V20  U20  V19  V18 ",
            g="AB22 AA22 AB21 AA21",
            b="Y21  Y20  AB20 AB19",
            hs="AA19", vs="Y19",
            attrs=Attrs(IOSTANDARD="LVCMOS33"),
        ),

        # User Push Bottons - Bank 34
        Resource("BTNC", 0, Pins("P16", dir="i"), Attrs(IOSTANDARD="LVCMOS18")),
        Resource("BTND", 0, Pins("R16", dir="i"), Attrs(IOSTANDARD="LVCMOS18")),
        Resource("BTNL", 0, Pins("N15", dir="i"), Attrs(IOSTANDARD="LVCMOS18")),
        Resource("BTNR", 0, Pins("R18", dir="i"), Attrs(IOSTANDARD="LVCMOS18")),
        Resource("BTNU", 0, Pins("T18", dir="i"), Attrs(IOSTANDARD="LVCMOS18")),

        # USB OTG VBus OC - Bank 34
        Resource("OTG_VBUSOC", 0, Pins("L16", dir="i"), Attrs(IOSTANDARD="LVCMOS18")),

        # Miscellaneous - Bank 34
        Resource("PUDC_B", 0, Pins("K16", dir="i"), Attrs(IOSTANDARD="LVCMOS18")),

        # USB OTG Reset - Bank 35
        Resource("OTG_RESETN", 0, Pins("G17", dir="i"), Attrs(IOSTANDARD="LVCMOS18")),

        # User DIP Switches - Bank 35
        *SwitchResources(pins={
            0: "F22",   # SW0
            1: "G22",   # SW1
            2: "H22",   # SW2
            3: "F21",   # SW3
            4: "H19",   # SW4
            5: "H18",   # SW5
            6: "H17",   # SW6
            7: "M15",   # SW7
        }, attrs=Attrs(IOSTANDARD="LVCMOS18")),

        # FMC Expansion Connector - Bank 13
        # FMC Expansion Connector - Bank 33
        # FMC Expansion Connector - Bank 34
        # FMC Expansion Connector - Bank 35
    ]

    connectors = [
                             #J1  J2   J3  J4      J7   J8   J9  J10
        Connector("pmod", 0, "Y11 AA11 Y10 AA9 - - AB11 AB10 AB9 AA8 - -"), # JA
        Connector("pmod", 1, "W12 W11  V10 W8  - - V12  W10  V9  V8  - -"), # JB
        Connector("pmod", 2, "AB6 ABA7 AA4 Y4  - - T6   R6   U4  T4  - -"), # JC
        Connector("pmod", 3, "W7  V7   V4  V5  - - W5   W6   U5  U6  - -"), # JD

        Connector("xadc", 0, {
            # XADC AD Channels - Bank 35
            "vaux0_n": "E16",
            "vaux0_p": "F16",
            "vaux8_n": "D17",
            "vaux8_p": "D16",

            # XADC GIO - Bank 34
            "gio0": "H15",
            "gio1": "R15",
            "gio2": "K15",
            "gio3": "J15",

            # XADC Inner Signals
            #"v_n": "M12",
            #"v_p": "L11",
            #"dx_n": "N12",  # Termal Diode diff pair N
            #"dx_p": "N11",  # Termal Diode diff pair P
        }),
    ]

    def __init__(self, bif=None):
        super().__init__(bif)

    def toolchain_prepare(self, products, name, **kwargs):
        overrides = {
            "": "",
        }
        return super().toolchain_prepare(products, name, **overrides, **kwargs)

    def toolchain_program(self, products, name, **kwargs):
        return super().toolchain_program(products, name, **kwargs)

class Zedboard(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        m.domains += ClockDomain("sync")
        m.submodules.ps = ps = ZedboardPS()

        cnt = Signal(29)
        m.d.sync += cnt.eq(cnt + 1)
        m.d.comb += ps.get_irq_signal(0).eq(cnt[-1])

        clk = ps.get_clock_signal(0, 200e6)
        m.d.comb += ClockSignal('sync').eq(clk)

        rst = ps.get_reset_signal(0)
        m.submodules.reset_sync = ResetSynchronizer(rst, domain="sync")

        return m

if __name__ == '__main__':

    bif = r"""
            all:
            {
                {{name}}.bit
            }
           """

    ZedboardPlatform(bif).build(elaboratable=Zedboard())
