import usb.core
import usb.util
import os,sys,time
import fcntl
import threading
from hidDefs import *

class RevolabsFLXInterface:

    ENDPOINT_ADDR_INTR_IN  = 0x84
    ENDPOINT_ADDR_INTR_OUT = 0x05
    ENDPOINT_ADDR_BULK_IN  = 0x87
    ENDPOINT_ADDR_BULK_OUT = 0x08

    KERNEL_PATH = "/dev/usb/hiddev0"

    def __init__(self):
        # find our device
        os.system("sudo chmod 777 " + RevolabsFLXInterface.KERNEL_PATH) #hack hack hack
        self.dev = open(RevolabsFLXInterface.KERNEL_PATH, "rb")
        
        self.rxCount = 0
        self.volUpButton = 0
        self.volDnButton = 0
        self.unk1        = 0
        self.phoneMute   = 0
        self.hookSwitch  = 0
        self.flash       = 0
        self.unk2        = 0

        self.unk1Prev    = 0
        self.unk2Prev    = 0

        self.callBtnPressCount = 0
        self.muteBtnPressCount = 0

        tmp = uint()
        tmp.get_version(self.dev)
        print("version 0x%x" % tmp.uint)
        tmp.get_flags(self.dev)
        tmp.uint = 3
        tmp.set_flags(self.dev)
        tmp.get_flags(self.dev)

        bgUpdateThread = threading.Thread(target = self.mainLoop, args = ())
        bgUpdateThread.daemon = True
        bgUpdateThread.start()

    def sendCmd(self, usage_code, val):
        tmp = hiddev_usage_ref()
        tmp.report_type = HID_REPORT_TYPE_OUTPUT
        tmp.report_id = HID_REPORT_ID_UNKNOWN
        tmp.usage_code = usage_code
        tmp.value = val
        tmp.set_usage_val(self.dev)

        tmp = hiddev_report_info()
        tmp.report_type = HID_REPORT_TYPE_OUTPUT
        tmp.report_id = 5
        tmp.num_fields = 1
        tmp.send_report(self.dev)

    def setLedsMuted(self):
        self.sendCmd(0x00080018, 0x0001)

    def setLedsUnmuted(self):
        self.sendCmd(0x00080018, 0x0000)

    def setOffHook(self):
        self.sendCmd(0x000b0020, 0x0000)

    def setOnHook(self):
        self.sendCmd(0x000b0020, 0x0001)

    def _getState(self):
        header = self.dev.read(4)
        value  = int.from_bytes(self.dev.read(4), byteorder='little')
        self.rxCount += 1
        if(header == b'\xe9\x00\x0c\x00'):
            self.volUpButton = value
        elif(header == b'\xea\x00\x0c\x00'):
            self.volDnButton = value
        elif(header == b'\x00\x00\x00\xff'):
            #?? Mute status state report? This is manufacturer specific
            self.unk1Prev = self.unk1
            self.unk1 = value
            if(self.unk1 != self.unk1Prev):
                if(self.unk1 == 0):
                    self.phoneMute = 0
                    self.muteBtnPressCount += 1
                elif(self.unk1 == 2):
                    self.phoneMute = 1
                    self.muteBtnPressCount += 1
                #else, ignore.

        elif(header == b'\x2f\x00\x0b\x00'):
            pass # not sure what info this has. It was supposedly phone mute. 

        elif(header == b'\x20\x00\x0b\x00'):
            self.hookSwitch = value

        elif(header == b'\x21\x00\x0b\x00'):
            self.flash = value

        elif(header == b'\x01\x00\x00\x00'):
            self.unk2Prev = self.unk2
            self.unk2 = value

            if(self.unk2 == 5 and self.unk2Prev != 5):
                self.callBtnPressCount += 1

        elif(header == b'\x00\x00\x00\x00'):
            pass #discard??

        elif(header == b'\xff\xff\xff\xff'):
            pass #discard??

        else:
            print("unknown header {:02x} {:02x} {:02x} {:02x} with value {}, skipping.".format(header[0], header[1], header[2], header[3], value))

    def _printState(self):
        print("{}| VolUP:{} | VolDn:{} | Unk1:{} "\
                "| Mute:{} | HookSw:{} | CallPrs:{} | Unk2:{}".format(
               self.rxCount,
               self.volUpButton,
               self.volDnButton,
               self.unk1,
               self.phoneMute,
               self.hookSwitch,
               self.callBtnPressCount,
               self.unk2))

    def mainLoop(self):
        while(True):
            self._getState()
            #self._printState()
            time.sleep(0.001)


## Test/Sandbox code
if __name__ == "__main__":
    testObj = RevolabsFLXInterface()
    testObj.setLedsMuted()
    while(True):
        testObj._printState()
        time.sleep(0.25)