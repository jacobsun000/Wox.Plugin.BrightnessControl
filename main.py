# -*- coding: utf-8 -*-
from wox import Wox
import ctypes
from ctypes import wintypes
import win32api

# Reference: https://zhuanlan.zhihu.com/p/110146413


class PHYSICAL_MONITOR(ctypes.Structure):
    _fields_ = [('hPhysicalMonitor', wintypes.HANDLE),
                ('szPhysicalMonitorDescription', ctypes.c_wchar * 128)]


class BrightnessControl(Wox):
    def __init__(self):
        Wox.__init__(self)
        self.monitors = self.get_monitor_info()

    def query(self, arg):
        def result(title, subtitle, n_monitor, h_monitor, brightness):
            return {
                'Title': f'{n_monitor}: {title}',
                'SubTitle': 'Current Brightness: {}%'.format(subtitle),
                'IcoPath': 'Images/app.png',
                'ContextData': title,  # Data that is passed to context_menu function call
                'JsonRPCAction': {
                    # Maps to function name that should be called if this action is selected.
                    'method': 'set_brightness',
                    # N number of params that will be passed to function call
                    'parameters': [h_monitor, brightness],
                }
            }

        monitor_id = -1
        brightness = 50
        if arg.strip() != "":
            monitor_id = int(arg.split(' ')[0])
            brightness = int(arg.split(' ')[1])

        monitors = filter(lambda a: monitor_id == -
                          1 or a[2] == monitor_id, self.get_monitor_info())
        return [result(*i, brightness) for i in monitors]

    def get_monitor_info(self):
        monitors = [i[0].handle for i in win32api.EnumDisplayMonitors()]
        result = []
        for i in range(len(monitors)):
            h_monitor = monitors[i]
            dxva2 = ctypes.windll.Dxva2
            nummons = wintypes.DWORD()
            dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(
                h_monitor, ctypes.byref(nummons))
            physical_monitors = (PHYSICAL_MONITOR * nummons.value)()
            dxva2.GetPhysicalMonitorsFromHMONITOR(
                h_monitor, nummons, physical_monitors)
            physical_monitor = physical_monitors[0]
            name = physical_monitor.szPhysicalMonitorDescription
            min_brightness = wintypes.DWORD()
            max_brightness = wintypes.DWORD()
            cur_brightness = wintypes.DWORD()
            dxva2.GetMonitorBrightness(physical_monitor.hPhysicalMonitor, ctypes.byref(
                min_brightness), ctypes.byref(cur_brightness), ctypes.byref(max_brightness))
            cur_brightness = cur_brightness.value
            result.append([name, cur_brightness, i, h_monitor])
        return result

    def set_brightness(self, h_monitor, brightness):
        dxva2 = ctypes.windll.Dxva2
        nummons = wintypes.DWORD()
        dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(
            h_monitor, ctypes.byref(nummons))
        physical_monitors = (PHYSICAL_MONITOR * nummons.value)()
        dxva2.GetPhysicalMonitorsFromHMONITOR(
            h_monitor, nummons, physical_monitors)
        physical_monitor = physical_monitors[0]
        dxva2.SetMonitorBrightness(
            physical_monitor.hPhysicalMonitor, brightness)


if __name__ == '__main__':
    BrightnessControl()
