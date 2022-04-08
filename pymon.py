# system
import os
import serial
import serial.tools.list_ports
import threading
import time
import sys
from datetime import datetime
from enum import Enum
from enum import auto
from typing import Union
# required
from readkeys import getch
# ?unused
# import msvcrt
# import unicodedata
# from tabulate import tabulate
# import textwrap
# from prompt_toolkit import prompt
# import glob

# system vars
VERSION = 0.7
CHAR_QUIT = 'q'
CHAR_HELP = 'h'
CHAR_INPUT = 'i'

CHAR_TIMESTAMP = 't'
CHAR_RENDER = 'r'
CHAR_SERIAL_FONT = 's'
CHAR_UNREDABLE = 'u'
CHAR_PORT = 'p'
CHAR_BAUD = 'b'
CHAR_LATENCY = 'l'
CHAR_BREAKLINE = 'z'
CHAR_DECODE = 'd'

CHAR_CONN_CLOSE = 'c'
CHAR_CONN_RECONN = 'O'
CHAR_CONN_MANUAL = 'o'
CHAR_CONN_FIND = 'f'

timestamp_arr = (0, 'milli')  # , 'micro')
timestamp = timestamp_arr.index('milli')

RENDER_ARR = ['hidden', 'up', 'down', 'left']
render = RENDER_ARR.index('down')
RENDER_OPT = (('0', 'H', 'hidden'), ('1', 'u', 'up'), ('2', 'd', 'down'),
              ('3', 'l', 'left'))

show_unredable = True
low_latency = True
breakline = True

last_line = ""
last_line_len = 0
line_break = True


class DECODE_MODE(Enum):
    UTF8 = 0
    UNICODE = auto()
    HEX = auto()
    DEC = auto()


decode_mode = DECODE_MODE.UTF8.value
DECODE_ARR = (
    'utf-8',
    'unicode-escape',
    # 'ascii',
    'raw_unicode_escape',
)
DECODE_OPT = (
    ('0', 'u', 'utf'),
    ('1', 'n', 'unicode'),
    # ('2', 'a', 'ascii'),
    # ('1', 'r', 'raw'),
    # ('0', 'r', 'txt'),
    ('2', 'h', 'hex'),
    ('3', 'd', 'dec'),
)


class INPUT_MODE(Enum):
    DISABLED = 0
    MESSAGE = 'msg'
    MESSAGE_EMPTY = 'msg_empty'
    BAUD = 'baud'
    PORT = 'port'
    RENDER = 'render'
    SERIAL_FONT = 'render serial'
    CONNECTION = 'connect'
    CONN_CLOSE = 'close'
    CONN_OPEN = 'open'
    CONN_MANUAL = 'manual'
    CONN_FIND = 'find'
    DECODE = 'decode'


input_mode = INPUT_MODE.DISABLED

# ? serial fonts - prevent non printable and dangerous chars in python
# _arr_ascii_ext_asciitable += "ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø×ƒáíóúñÑªº¿®¬½¼¡«»░▒▓│┤ÁÂÀ©╣║╗╝¢¥┐"
# _arr_ascii_ext_asciitable += "└┴┬├─┼ãÃ╚╔╩╦╠═╬¤ðÐÊËÈıÍÎÏ┘┌█▄¦Ì▀ÓßÔÒõÕµþÞÚÛÙýÝ¯´≡±‗¾¶§÷¸°¨·¹³²■"
_arr_ascii_ext_dos = ""
#                      ░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀
_arr_ascii_ext_dos += "€┤‚ƒ„┼†‡ˆ‰Š‹Œ╜Ž┐└‘’“”•–╪˜™š›œ├žŸ╓" "¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿"
_arr_ascii_ext_dos += "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"
_arr_ascii_ext_asciitable = ""
mpa_ascii_ext_dos = {}
# for x in _arr_ascii_ext_dos:
#     mpa_ascii_ext_dos[_arr_ascii_ext_dos.index(x)+128] = x
for x in range(128, 161):
    mpa_ascii_ext_dos[x] = _arr_ascii_ext_dos[x - 128]

# print(mpa_ascii_ext)
# print(ord('ã'))
mpa_symbol = {}
mpa_symbol.update(mpa_ascii_ext_dos)
mpa_symbol[0] = chr(9826)  # ␀ '♢' null
mpa_symbol[7] = chr(9679)  # ␇ '●' bell
mpa_symbol[8] = chr(9689)  # ␈ '◙' backspace
# mpa_symbol[9] = chr(9675)         #?␉ '○' horizontal tab
mpa_symbol[11] = chr(9794)  # ?␋ '♂' vertical tab
mpa_symbol[12] = chr(9792)  # ?␌ '♀' form feed
mpa_symbol[13] = None  # ␍ '♪' carriage return 9834 -> ''
mpa_symbol[14] = chr(9835)  # ␎ '♫' shift out
mpa_symbol[15] = chr(9788)  # ␏ '☼' shift in
mpa_symbol[27] = chr(8592)  # ␛ '←' esc
mpa_symbol[127] = chr(8962)  # ␡ '⌂' delete
mpa_symbol_ext = {}
mpa_symbol_ext[255] = chr(9686)  # '◖'   non-breaking space

mpa_text = {}
mpa_text.update(mpa_ascii_ext_dos)
for x in range(32):
    mpa_text[x] = chr(x + 9216)  # '␀'   character unicode range
del mpa_text[9]  # !␉ '○' horizontal tab
mpa_text[13] = None  # ␍ '♪' carriage return 9834 -> ''
mpa_text[127] = chr(9249)  # ␡
mpa_text_ext = {}
for x in range(160, 256):
    mpa_text[x] = chr(x + 9216)  # '␀'   character unicode range
mpa_text_ext[255] = mpa_symbol_ext[255]

mpa_arduino = {}
for x in range(32):
    mpa_arduino[x] = "▯"
mpa_arduino[13] = None  # ␍ '♪' carriage return 9834 -> ''
for x in range(127, 160):
    mpa_arduino[x] = "⸮"
del mpa_arduino[9]  # horizontal tab
del mpa_arduino[10]  # line feed
mpa_arduino_ext = {}
# for x in range(160, 256):
#     mpa_arduino[x] = "⸮"
mpa_arduino_ext[255] = "⸮"

SERIAL_FONT_ARR = [mpa_symbol, mpa_text, mpa_arduino]
SERIAL_FONT_EXT_ARR = [mpa_symbol_ext, mpa_text_ext, mpa_arduino_ext]
SERIAL_FONT_OPT = (('0', 's', 'symbol'), ('1', 't', 'text'), ('2', 'a',
                                                              'arduino'))
serial_font = 2

ms_read = datetime.now()


class Ports:

    class STATUS(Enum):
        MISSING = 'MISSING'
        BUSY = 'BUSY'
        AVAILABLE = 'AVAIABLE'
        CONNECTED = 'CONNECTED'
        BLACKLIST = 'BLACKLIST'
        IGNORED = 'IGNORED'

    status_ports = []
    status_serials = []

    class CONNECTION(Enum):
        MANUAL = 'MANUAL'
        RECONNECT = 'RECONNECT'
        FIND = 'FIND'

    connection_mode = CONNECTION.FIND

    serials = [serial.Serial()]
    list = []

    list_names = []
    blacklist = ["COM1"]

    def upgrade(self):
        if self.connection_mode != self.CONNECTION.MANUAL:
            self.serial_open()

    def update(self, upgrade=True, try_blacklist=False, try_all=False):
        self.list = serial.tools.list_ports.comports(include_links=False)
        self.list_names = [port.name for port in self.list]

        # ports
        self.status_ports.clear()
        # anchor update
        # if(self.status_serials):
        #     print(self.status_serials[0], datetime.now())
        for port in self.list:
            if try_blacklist == False and port.name in self.blacklist:
                port_status = self.STATUS.BLACKLIST

            elif self.connection_mode != Ports.CONNECTION.FIND:
                port_status = self.STATUS.IGNORED
                for ser in self.serials:
                    if ser.port == port.name:
                        if ser.isOpen():
                            port_status = self.STATUS.CONNECTED
                        else:
                            try:
                                s = serial.Serial(port.name)
                                s.close()
                                port_status = self.STATUS.AVAILABLE
                            except (OSError, serial.SerialException):
                                port_status = self.STATUS.BUSY

            else:
                try:
                    s = serial.Serial(port.name)
                    s.close()
                    port_status = self.STATUS.AVAILABLE
                except (OSError, serial.SerialException):
                    port_status = self.STATUS.BUSY
                    for ser in self.serials:
                        if ser.port == port.name and ser.isOpen():
                            port_status = self.STATUS.CONNECTED
                        break
            self.status_ports.append(port_status)

        # serials
        self.status_serials.clear()

        for ser in self.serials:
            ser_port = [port for port in self.list if ser.port in port.name]
            if ser_port:
                ser_status = self.status_ports[self.list.index(ser_port[0])]
            else:
                ser_status = self.STATUS.MISSING
                ser.close()
            self.status_serials.append(ser_status)

        if upgrade:
            self.upgrade()

    def __init__(self):
        self.serials.clear()
        self.update()

    def serial_add(self, *args, **kwargs):
        ser = serial.Serial()
        # args
        for arg in args:
            if type(arg) is str:
                ser.port = arg
            elif type(arg) is int:
                ser.baudrate = arg
        # kwargs
        kwarg = kwargs.get('baudrate')
        if kwarg:
            ser.baudrate = kwarg
        kwarg = kwargs.get('port')
        if kwarg:
            ser.port = kwarg
        kwarg = kwargs.get('bytesize')
        if kwarg:
            ser.bytesize = kwarg
        kwarg = kwargs.get('parity')
        if kwarg:
            ser.parity = kwarg
        kwarg = kwargs.get('stopbits')
        if kwarg:
            ser.stopbits = kwarg
        kwarg = kwargs.get('timeout')
        if kwarg:
            ser.timeout = kwarg

        if not ser.port:
            ser.setPort(' ')

        ser_ports = [x for x in self.serials if ser.ports in x.name]
        ret = False

        if not ser_ports:
            self.serials.append(ser)
            ret = True

        self.update()
        return ret

    def serial_del(self, index: Union[serial.Serial, int]):
        ret = True
        if type(index) is int and 0 <= index < len(self.serials):
            del self.serials[index]
        elif type(index) is serial.Serial and self.serials.index(index):
            self.serials.remove(index)
            self.update()
        else:
            ret = False
        return ret

    def serial_open(self, index: Union[serial.Serial, int] = None, con=None):
        if not len(self.serials):
            return 1
        # print(ports.status_ports)
        # print(ports.list_names)

        if type(con) is not self.CONNECTION:
            con = self.connection_mode
        if index:
            if type(index) is int and 0 <= index < len(self.serials):
                ser = self.serials[index]
                # ser_index = index
            elif type(index) is serial.Serial and self.serials.index(index):
                ser = index
        else:
            ser = None

        if ser and ser.isOpen():
            return 2

        if con == Ports.CONNECTION.MANUAL:
            self.update()

        if con == Ports.CONNECTION.FIND:
            ret = 3
            # open ser
            if ser:
                if ser.port in self.list_names and not ser.isOpen():
                    ser.open()
                    ret = 0
            # open all
            if ret:
                # print("open all")
                for ser in self.serials:
                    ser_stats = self.getStatusSerial(ser)
                    if ser.port in self.list_names:
                        if not ser.isOpen(
                        ) and ser_stats == Ports.STATUS.AVAILABLE:
                            try:
                                ser.open()
                            except:
                                print("erro serial_open: 4")
                                # os._exit(4)
                            ret = 0
                    else:
                        for port in self.list:
                            for block in self.blacklist:
                                status = self.status_ports[self.list.index(
                                    port)]
                                if port.name != block and status == Ports.STATUS.AVAILABLE:
                                    if not ser.isOpen():
                                        ser.port = port.name
                                        try:
                                            ser.open()
                                        except:
                                            print("erro serial_open: 5")
                                            # os._exit(2)
                                        ret = 0
                ser = None
        else:
            ret = 6
            if ser:
                status = self.status_ports[self.list_names.index(
                    ser.port)] if ser.port in self.list_names else False
                if ser.port in self.list_names and status == Ports.STATUS.AVAILABLE:
                    ser.open()
                    ret = 0
            else:
                for ser in self.serials:
                    try:
                        status = self.status_ports[self.list_names.index(
                            ser.port
                        )] if ser.port in self.list_names else False
                        if status and ser.port in self.list_names and status == Ports.STATUS.AVAILABLE:
                            ser.open()
                            ret = 0
                    except:

                        print("ser = ", ser.port)
                        print("list = ", self.list)
                        print("list_names = ", self.list_names)
                        os._exit(1)
                        status = self.status_ports[self.list_names.index(
                            ser.port)]

        self.update(False)
        return ret

    def serial_close(self, index: Union[serial.Serial, int]):
        ser = None
        if type(index) is int and 0 <= index < len(self.serials):
            ser = self.serials[index]
            ser_index = index
        elif type(index) is serial.Serial and self.serials.index(index):
            ser = index
            ser_index = self.serials.index(index)

        if not ser:
            return 1
        if not ser.isOpen():
            return 2

        ser.close()
        self.update()
        return 0

    def getStatusSerial(self, index: Union[serial.Serial, int]):
        ser = None
        if type(index) is int and 0 <= index < len(self.serials):
            ser = self.serials[index]
            ser_index = index
        elif type(index) is serial.Serial:
            ser = index
            ser_index = self.serials.index(index)

        if not ser:
            return 1

        ser_status = self.status_serials[ser_index]
        return ser_status


class ListenOnSerialPort(threading.Thread):

    def __init__(self, keyboard_thread):
        threading.Thread.__init__(self)
        self.keyboard_thread = keyboard_thread

    def run(self):
        # anchor timer
        switch_input = False
        switch_conn = False
        print_serial = False
        ms_1 = datetime.now()
        while True:
            global input_mode
            if not ((datetime.now() - ms_1).microseconds < 10000
                    and ports.serials[0].isOpen() == False
                    and print_serial == False):
                if not input_mode.value:
                    if switch_input != input_mode or switch_conn != ports.getStatusSerial(
                            0):
                        switch_input = input_mode
                        switch_conn = ports.getStatusSerial(0)
                        print_serial = footer(True)
                    else:
                        print_serial = footer()
                elif switch_input != input_mode:
                    print_serial = footer(True)
                    switch_input = input_mode
                ms_1 = datetime.now()
            else:
                time.sleep(0.1)
            time.sleep(0.0000001)


class ListenOnKeyboard(threading.Thread):
    # input_bkp = ""
    def run(self):
        while True:
            global input_mode
            try:
                cmd_in = getch()
                # sys.stdin.read()
                if not input_mode.value:
                    if cmd_in == CHAR_INPUT:
                        input_mode = INPUT_MODE.MESSAGE
                        string = input("")
                        if len(string):
                            ports.serials[0].write(string.encode())
                        else:
                            # col = os.get_terminal_size().columns
                            print("\033[F\033[K", end='')

                    if cmd_in.lower() == CHAR_TIMESTAMP:
                        global timestamp
                        timestamp_new = timestamp + 1 if cmd_in == CHAR_TIMESTAMP.lower(
                        ) else timestamp - 1
                        timestamp = ((timestamp_new) % len(timestamp_arr))
                    if cmd_in.lower() == CHAR_RENDER:
                        global render
                        render_new = render + 1 if cmd_in == CHAR_RENDER.lower(
                        ) else render - 1
                        render = ((render_new) % len(RENDER_ARR))
                    if cmd_in == CHAR_UNREDABLE:
                        global show_unredable
                        show_unredable = not show_unredable
                    if cmd_in == CHAR_LATENCY:
                        global low_latency
                        low_latency = not low_latency
                    if cmd_in == CHAR_BREAKLINE:
                        global breakline
                        breakline = not breakline
                    if cmd_in == CHAR_QUIT:
                        ports.serials[0].close()
                        os._exit(1)
                    if cmd_in == CHAR_HELP:
                        print("HELP")
                        ln_count = 0
                        ln_count += print_help_options()
                        ln_count += print_help_usage()
                        print()
                        # ln = "\033[F\033[K".join("" for x in range(ln_count))
                        # print("\033[%dD" % col, ln)
                        # g = getch()
                        ports.update()

                    if cmd_in == CHAR_PORT:
                        input_mode = INPUT_MODE.PORT
                        string = input()
                        if len(string):
                            ports.serials[0].port = string
                            ports.update()
                        else:
                            col = os.get_terminal_size().columns
                            print("\033[%dD\033[K\033[F\033[K\033[F\033[K" %
                                  col,
                                  end='')
                    if cmd_in == CHAR_BAUD:
                        input_mode = INPUT_MODE.BAUD
                        string = input("")
                        if len(string):
                            ports.serials[0].baudrate = int(string)
                            ports.update()
                        else:
                            col = os.get_terminal_size().columns
                            ln = "\033[F\033[K".join("" for x in range(3))
                            i = 108
                            while col < i:
                                ln += "\033[F\033[K"
                                i /= 2
                            print("\033[%dD" % col, ln, end='')
                    if cmd_in == CHAR_SERIAL_FONT:
                        input_mode = INPUT_MODE.SERIAL_FONT
                        string = input("")
                        arr = [x for x in SERIAL_FONT_OPT if string in x]
                        if arr:
                            global serial_font
                            serial_font = int(SERIAL_FONT_OPT.index(arr[0]))
                        else:
                            col = os.get_terminal_size().columns
                            ln = "\033[F\033[K".join("" for x in range(7))
                            print("\033[%dD" % col, ln, end='')
                    if cmd_in == CHAR_DECODE:
                        input_mode = INPUT_MODE.DECODE
                        string = input("")
                        arr = [x for x in DECODE_OPT if string in x]
                        if arr:
                            global decode_mode
                            decode_mode = DECODE_OPT.index(arr[0])
                            # global decode_mode
                            # decode_mode = 3
                        else:
                            col = os.get_terminal_size().columns
                            ln = "\033[F\033[K".join("" for x in range(2 + 1))
                            print("\033[%dD" % col, ln, end='')

                    if cmd_in == CHAR_CONN_CLOSE:
                        input_mode = INPUT_MODE.CONN_CLOSE
                        ports.connection_mode = Ports.CONNECTION.MANUAL
                        ports.serial_close(0)
                    if cmd_in == CHAR_CONN_MANUAL:
                        ports.connection_mode = Ports.CONNECTION.MANUAL
                        input_mode = INPUT_MODE.CONN_MANUAL
                        ports.serial_open()
                    if cmd_in == CHAR_CONN_RECONN:
                        ports.connection_mode = Ports.CONNECTION.RECONNECT
                        ports.update()
                    if cmd_in == CHAR_CONN_FIND:
                        ports.connection_mode = Ports.CONNECTION.FIND
                        ports.update()
            except:
                True
            input_mode = INPUT_MODE.DISABLED
            footer(True)


def serial_decode(read):
    global decode_mode
    line_break_next = False
    ser_in = ""
    try:
        if decode_mode in (DECODE_MODE.UTF8.value, DECODE_MODE.UNICODE.value):
            dec = read.decode(DECODE_ARR[decode_mode], 'replace')
        else:
            dec = read.decode(DECODE_ARR[1], 'replace')
        # dec = unicodedata.normalize('NFC', dec)
        ser_in = dec
        if ser_in[-1:] == '\n':
            ser_in = ser_in.strip('\n')
            line_break_next = True
    except:
        if show_unredable:
            dec = read.decode(DECODE_ARR[1], 'replace')
            ser_in = dec
            if ser_in[-1:] == '\n':
                ser_in = ser_in.strip('\n')
                line_break_next = True

    if decode_mode in (DECODE_MODE.UTF8.value, DECODE_MODE.UNICODE.value):
        ser_in = ser_in.translate(SERIAL_FONT_ARR[serial_font])
        if decode_mode == DECODE_MODE.UTF8.value:
            ser_in = ser_in.translate(SERIAL_FONT_EXT_ARR[serial_font])
    if decode_mode == DECODE_MODE.HEX.value:
        ser_in = "".join("{:02x} ".format(ord(c)) if c != '\n' else '\n'
                         for c in ser_in)
    if decode_mode == DECODE_MODE.DEC.value:
        ser_in = "".join("{} ".format(ord(c) if c != '\n' else '\n')
                         for c in ser_in)[1:]

    return str(ser_in), bool(line_break_next)


def footer(force_update=False):
    global ports
    global timestamp
    global line_break
    global last_line
    global last_line_len
    global low_latency
    global ms_read
    global breakline
    line_break_next = False
    port = ports.serials[0].port
    update_footer = force_update
    print_serial = False
    ser_in = ""
    line_break_chars = '\r\n'
    remove_chars = '\r\b\127'

    # render input
    try:
        if ports.serials[0].isOpen():
            if ports.serials[0].inWaiting():
                try:
                    read = ports.serials[0].read_all(
                    ) if low_latency else ports.serials[0].readline()
                    ser_in, line_break_next = serial_decode(read)
                    # ser_in = ret_str()
                    # line_break_next = ret_bol()
                except (OSError, serial.SerialException):
                    if ports.getStatusSerial(0) is Ports.STATUS.CONNECTED:
                        update_footer = True
        else:
            ports.update()
            last_line = ""
            last_line_len = 0
    except (OSError, serial.SerialException):
        ports.update()
        last_line = ""
        last_line_len = 0
        update_footer = True

    port_status = ports.getStatusSerial(0)
    if port_status is Ports.STATUS.CONNECTED and ser_in:
        print_serial = True
    elif not update_footer:
        return print_serial
        # ? prevent unclickable links

    # render timestamp
    footer_time = datetime.now().strftime("%H:%M:%S.%f")
    if timestamp == timestamp_arr.index('milli'):
        footer_time = footer_time[:-3]

    # render indicator
    port_indicator = 'c'
    if port_status is Ports.STATUS.AVAILABLE:
        port_indicator = 'o'
    if port_status is Ports.STATUS.BUSY:
        port_indicator = 'x'
    if port_status is Ports.STATUS.MISSING:
        port_indicator = '?'
    if port_status is Ports.STATUS.BLACKLIST:
        port_indicator = '!'
    if port_status is Ports.STATUS.IGNORED:
        port_indicator = 'i'

    col = os.get_terminal_size().columns
    # lin = os.get_terminal_size().lines

    # render serial
    ser_pr = ""
    if print_serial:
        timestamp_text = "[%s] << " % footer_time
        # if breakline and timestamp:
        #     ser_in = textwrap.fill(ser_in, col-len(timestamp_text))
        if render == RENDER_ARR.index('up'):
            # if line_break:
            print()
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
        if render == RENDER_ARR.index('down'):
            if not line_break:
                sys.stdout.write("\033[F" + "\033[1B" + "\033[K")
            else:
                sys.stdout.write("\n\033[F" + "\033[K")
        if render == RENDER_ARR.index('left'):
            sys.stdout.write("\033[F" + "\033[1B" + "\033[K")
            # print("\033[%dD\033[K" % col, end='')
        # print serial
        # if last_line_len > 25:
        #     print("<L", last_line_len, ">")
        if not line_break:
            # sys.stdout.write("\033[1A\033[%dC" % 90 + "%d" % last_line_len)
            if (datetime.now() - ms_read).microseconds < 1 * 100000:
                sys.stdout.write("\033[1A")
                sys.stdout.write(last_line)
            else:
                sys.stdout.write("\033[1A\033[%dC" % (last_line_len))
            # sys.stdout.write("\033[u")
        if timestamp:
            if line_break:
                ser_pr += timestamp_text
            # else:
            #     ser_pr += "+>"
            ser_pr += ser_in
            ser_pr = ser_pr.replace('\n', '\n' + timestamp_text)
        else:
            ser_pr += ser_in
        sys.stdout.write(ser_pr + "\033[s" + "\n")

        print_serial = True
        last_line = ser_pr
        while '\n' in last_line:
            last_line = last_line[last_line.index('\n') + 1:]
        if line_break:
            last_line_len = len(last_line)
        else:
            last_line_len += len(last_line)
        line_break = line_break_next

    # render footer
    footer_ini = ">> PyMon"
    footer_port = " [%s %c]" % (port, port_indicator)
    # footer_render = " render[%d]" % (render)
    footer_render = " render[%s]" % (RENDER_ARR[render])
    footer_baud = "  baud [%d]" % (ports.serials[0].baudrate)
    footer_help = "  Type  h [help]"
    footer_cmd = "  Cmd >>"
    # footer_input = "  Input [%s] >> " % _input_mode.value
    footer_input = "  Input mode >>"
    ret = footer_ini

    # render imput
    global input_mode
    _input_mode = input_mode
    if _input_mode == INPUT_MODE.PORT:
        print("\033[%dD\033[K>> Ports:" % col, ports.list_names)
        # print_ports()

    if _input_mode == INPUT_MODE.BAUD:
        print("\033[%dD\033[K>> Bauds:" % col, serial.Serial.BAUDRATES)
    if _input_mode == INPUT_MODE.SERIAL_FONT:
        print("\033[%dD\033[K>> Serial fonts:" % col)
        print_serial_fonts()
    if _input_mode == INPUT_MODE.DECODE:
        print("\033[%dD\033[K>> Decode mode:" % col, end='')
        print_decode_mode()
    # if _input_mode == INPUT_MODE.MESSAGE_EMPTY:
    #     print("\033[%dD\033[K\033[F\033[K" % col)

    if _input_mode.value:
        ret += footer_input
    else:
        ret += footer_port + footer_baud + footer_cmd

    # anchor footer print
    # print footer
    if render is not RENDER_ARR.index('hidden'):
        if print_serial or update_footer:
            print("\033[%dD\033[K%s" % (col, ret), end='')
            # print("\033[%dD\033[K%s" % (col, ret),datetime.now(), end='')
    if port_status is Ports.STATUS.CONNECTED and ser_in:
        ms_read = datetime.now()
    return print_serial


def print_decode_mode():
    print(str(DECODE_OPT)[1:-1])
    return 0


def print_serial_fonts():
    str_pr = "'0', 's', 'symbol'    |" + mpa_symbol[0] + "  |" + chr(1) + "  |" + chr(2) + "  |" + \
        "a  |b  |c  |" + mpa_symbol[127] + "  |" + \
        _arr_ascii_ext_dos[60] + "  |" + _arr_ascii_ext_dos[-1] + "  |\n"

    str_pr += "'1', 't', 'text'      |" + \
        mpa_text[0] + "  |" + mpa_text[1] + "  |" + mpa_text[2] + "  |" + \
        "a  |b  |c  |" + \
        mpa_text[127] + "  |" + _arr_ascii_ext_dos[60] + \
        "  |" + _arr_ascii_ext_dos[-1] + "  |\n"

    str_pr += "'2', 'a', 'arduino'   |" + \
        mpa_arduino[0] + "  |" + mpa_arduino[1] + "  |" + mpa_arduino[2] + "  |" + \
        "a  |b  |c  |" + \
        mpa_arduino[127] + "  |" + _arr_ascii_ext_dos[60] + \
        "  |" + mpa_arduino_ext[255] + "  |\n"

    str_pr += "- character code -    |0  |1  |2  |97 |98 |99 |127|188|255|" + "\n"

    print(str_pr, end='')
    return len(str_pr)


def print_help_options():
    print("Options:")
    print("-h --help                Show help")
    print("-v --version             Show version and exit")
    print("-l --list                List all serial ports avaiable")
    print("-t --timeout             Set the serial port timeout (default 1s)")
    return 5


def print_help_usage(simple_mode=False):
    print("Usage:")
    print("[%s] help" % CHAR_HELP, end='   ')
    print("[%s] quit" % CHAR_QUIT, end='  ')
    print("[%s] port" % CHAR_PORT, end='  ')
    print("[%s] baud" % CHAR_BAUD)
    print("[%s] input to serial" % CHAR_INPUT, end='  ')
    print("[%s] timestamp" % CHAR_TIMESTAMP, end='')
    print()
    ln = 8
    if not simple_mode:
        print("[%s][%s] render mode  " % (CHAR_RENDER.upper(), CHAR_RENDER),
              RENDER_ARR)
        print()
        print("[%s] close port           Connection mode -> manual" %
              CHAR_CONN_CLOSE)
        print("[%s] open port            Connection mode -> manual" %
              CHAR_CONN_MANUAL)
        print("[%s] auto open port       Connection mode -> auto" %
              CHAR_CONN_RECONN)
        print("[%s] find and open        Connection mode -> find" %
              CHAR_CONN_FIND)

        print("[%s] serial font" % CHAR_SERIAL_FONT, end='      ')
        print("[%s] decode mode" % CHAR_DECODE)
        ln += 8
    return ln


def print_ports():
    ports.update(False, False)
    for name in ports.list_names:
        print(name, "-",
              ports.status_ports[ports.list_names.index(name)].value)


# main app
ports = Ports()
port = "port"
baud = 115200  # default value
timeout_ = 0.3
n = len(sys.argv)
# init options
if n > 1 and any(x in sys.argv[1] for x in ["-l", "l", "--list", "list"]):
    ports.update(False, False)
    for name in ports.list_names:
        print(name, "-",
              ports.status_ports[ports.list_names.index(name)].value)
    # print(ports.list_names)
    os._exit(1)
if n > 1 and any(x in sys.argv[1] for x in ["-v", "--version"]):
    print("PyMon", VERSION)
    os._exit(1)
if n > 1 and any(x in sys.argv[1] for x in ["-h", "--help"]):
    print_help_options()
    print_help_usage()
    os._exit(1)

else:
    # init parameters
    for i in range(1, n):
        # port
        if i < n and any(x in sys.argv[i] for x in ["-p", "--port"]):
            # if sys.argv[i] == "-p" and i < n or sys.argv[i] == "--port" and i < n:
            port = sys.argv[i + 1].upper()
        # baud
        if i < n and any(x in sys.argv[i] for x in ["-b", "--baud"]):
            baud = sys.argv[i + 1]
        # timeout
        if i < n and any(x in sys.argv[i] for x in ["-t", "--timeout"]):
            timeout_ = sys.argv[i + 1]

# if port == None:
#     port = prompt("port: ")
# if baud == None:
#     baud = input("baud: ")

# imp = prompt("Texto:", default="abc")

print_help_usage(True)
print()

ports.serial_add(port, baud, timeout=timeout_)
# print(ports.status_ports)
# print(ports.list_names)

kb_listen = ListenOnKeyboard()
kb_listen.start()

footer(True)

sp_listen = ListenOnSerialPort(kb_listen)
sp_listen.start()
