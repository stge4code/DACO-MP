#!/usr/bin/env python
import serial
import time
import encodings
import unicodedata, re, sys
import pickle

special_noprint = "\x5B\x0D\x51"
all_chars = (unichr(i) for i in xrange(0x110000))
control_chars = ''.join(map(unichr, range(0, 32) + range(127, 160)))
control_chars += special_noprint
control_char_re = re.compile('[%s]' % re.escape(control_chars))


def remove_control_chars(s):
    return control_char_re.sub('', s)


class Daco():
    def __init__(self):
        self.dumpfile = "/home/mar345/daco.pickle"
        self.portname = None
        self.delta = None
        self.count = None
        try:
            dacodump = self.loaddata()
            self.delta = dacodump["delta"]
            self.count = dacodump["count"]
            self.portname = dacodump["portname"]
        except:
            self.delta = 0.5
            self.count = 3
            self.portname = '/dev/ttyS0'
        self.port = serial.Serial(self.portname, baudrate=2400, timeout=0, bytesize=serial.EIGHTBITS,
                                  stopbits=serial.STOPBITS_ONE)

    def loaddata(self):
        with open(self.dumpfile, "rb") as file:
            dacodump = pickle.load(file)
        return dacodump

    def makedump(self):
        dacodump = {
            "delta": self.delta,
            "count": self.count,
            "portname": slef.portname
        }
        return dacodump

    def savedata(self):
        with open(self.dumpfile, "wb") as file:
            pickle.dump(self.makedump(), file)

    def makecommand(self, command_):
        command = "\x01" + command_.upper() + "\x0D"
        return command

    def setinterruption(self, delta_, count_):
        self.delta = delta_
        self.count = count_

    def sendstopcommand(self):
        self.port.write("\x05")

    def start(self):
        self.port.open()

    def run(self):
        self.port.open()
        self.sendstopcommand()
        self.port.write(self.makecommand("PG0"))
        self.response(False)
        self.port.write(self.makecommand("RC"))
        self.response(False)
        self.port.write(self.makecommand("DA"))
        self.response(False)
        self.port.write(self.makecommand("DA10,18,96"))
        self.response(False)
        self.port.write(self.makecommand("TM12,35,12"))
        self.response(False)
        self.port.write(self.makecommand("MP"))
        self.response(False)

    def end(self):
        try:
            self.port.close()
        except Exception:
            pass

    def sendcommand(self, command_, printmode_=True):
        if command_ == "connect":
            self.run()
        elif "interruption " in command_:
            tmp = [x for x in command_.replace("interruption ", '').split()]
            self.setinterruption(float(tmp[0]), int(tmp[1]))
            self.savedata()
        else:
            self.port.write(self.makecommand(command_))
            self.response(printmode_)

    def response(self, printmode_=True):
        count = self.count
        response = ''
        while count > 0:
            self.sendstopcommand()
            time.sleep(self.delta)
            response = remove_control_chars(self.port.read(self.port.inWaiting())).strip()
            if printmode_:
                if response != '': print
                response
            count -= 1


if __name__ == "__main__":
    daco = Daco()
    daco.start()
    if len(sys.argv) > 1:
        daco.sendcommand(sys.argv[1])
    else:
        command = raw_input()
        while command != "disconnect":
            daco.sendcommand(command)
            command = raw_input()
    daco.end()
