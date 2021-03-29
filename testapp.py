#!/usr/bin/env python3

import wx

import matplotlib as mpl
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar)

import wx.lib.agw.aui as aui
import wx.lib.mixins.inspection as wit

import numpy as np
import scipy as sp
from scipy import signal
from scipy.signal import argrelextrema


def switch_demo(argument, c):
    y = {
        1: np.sin(c * 2.0 * np.pi * x),
        2: signal.square(c * 2.0 * np.pi * x),
        3: signal.sawtooth(1.0 * 2.0 * np.pi * x)
    }
    return y.get(argument)


class Plot(wx.Panel):
    def __init__(self, parent, id=-1, dpi=None, **kwargs):
        super().__init__(parent, id=id, **kwargs)
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2, 2))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        # slider = Example()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)

        pnl_sizer = wx.GridBagSizer(5, 5)
        pnl = wx.Panel(self)
        self.sld = wx.Slider(pnl, value=10, minValue=1, maxValue=100, style=wx.SL_HORIZONTAL)
        # sizer.Add(self.slider, 2, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.sld.Bind(wx.EVT_SCROLL, self.OnSliderScroll)
        pnl_sizer.Add(self.sld, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=1)
        self.txt = wx.StaticText(pnl, label='10')
        pnl_sizer.Add(self.txt, pos=(0, 1), flag=wx.TOP | wx.RIGHT, border=1)
        pnl_sizer.AddGrowableCol(0)
        pnl.SetSizer(pnl_sizer)
        sizer.Add(pnl, 0, wx.LEFT | wx.EXPAND)
        fslider = FloatSlider(self, -1, 0.2, 0.10004, 1.00008, 1e-4)
        sizer.Add(fslider, 0, wx.LEFT | wx.EXPAND)
        self.Centre()
        print(type(self.sld.GetValue()))

    def RetVal(self):
        return self.sld.GetValue()

    def OnSliderScroll(self, e):
        obj = e.GetEventObject()
        val = obj.GetValue()
        self.txt.SetLabel(str(val))


class PlotNotebook(wx.Panel):
    def __init__(self, parent, id=-1):
        super().__init__(parent, id=id)
        self.nb = aui.AuiNotebook(self)
        sizer = wx.BoxSizer()
        self.fslider = FloatSlider(self, -1, 1, 1, 100, 1)
        sizer.Add(self.fslider, 0, wx.LEFT | wx.EXPAND)
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def add(self, name="plot"):
        page = Plot(self.nb)
        self.nb.AddPage(page, name)
        return page.figure


class FloatSlider(wx.Slider):
    def __init__(self, parent, id, value, minval, maxval, res,
                 size=wx.DefaultSize, style=wx.SL_HORIZONTAL,
                 name='floatslider'):
        self._value = value
        self._min = minval
        self._max = maxval
        self._res = res
        ival, imin, imax = [round(v / res) for v in (value, minval, maxval)]
        self._islider = super(FloatSlider, self)
        self._islider.__init__(
            parent, id, ival, imin, imax, size=size, style=style, name=name
        )
        self.Bind(wx.EVT_SCROLL, self._OnScroll)

    def _OnScroll(self, event):
        ival = self._islider.GetValue()
        imin = self._islider.GetMin()
        imax = self._islider.GetMax()
        if ival == imin:
            self._value = self._min
        elif ival == imax:
            self._value = self._max
        else:
            self._value = ival * self._res
        event.Skip()
    # print 'OnScroll: value=%f, ival=%d' % (self._value, ival)

    def GetValue(self):
        return self._value

    def GetMin(self):
        return self._min

    def GetMax(self):
        return self._max

    def GetRes(self):
        return self._res

    def SetValue(self, value):
        self._islider.SetValue(round(value / self._res))
        self._value = value

    def SetMin(self, minval):
        self._islider.SetMin(round(minval / self._res))
        self._min = minval

    def SetMax(self, maxval):
        self._islider.SetMax(round(maxval / self._res))
        self._max = maxval

    def SetRes(self, res):
        self._islider.SetRange(round(self._min / res), round(self._max / res))
        self._islider.SetValue(round(self._value / res))
        self._res = res

    def SetRange(self, minval, maxval):
        self._islider.SetRange(round(minval / self._res), round(maxval / self._res))
        self._min = minval
        self._max = maxval


# Number of sample points
N = 5000
# sample spacing
T = 1.0 / 800.0
x = np.linspace(0.0, N * T, N, endpoint=False)



def demo():
    temp = 0
    app = wx.App()

    frame = wx.Frame(None, -1, 'Plotter')
    plotter = PlotNotebook(frame)
    war = plotter.fslider.GetValue()
    y = switch_demo(2, 21)

    yf = np.fft.fft(y)
    xf = np.fft.fftfreq(N, T)[:N // 2]
    res = max(20 / N * np.abs(yf[0:N // 2]))
    z = argrelextrema(2.0 / N * np.abs(yf[0:N // 2]), np.greater, 0, war)
    z = np.concatenate(np.asarray(z))
    zy = np.ones(len(z)) * (2.0 / N * np.abs(yf[z]))
    s = np.zeros(len(z))


    axes1 = plotter.add('Signal').gca()
    axes1.plot(x, y)
    axes1.plot(x, -y)
    axes1.plot(x + 0.1, y - 0.5 * y)
    axes1.grid(True, which='both')

    if(war!=temp):
        temp=war
        print(temp)

    axes2 = plotter.add('FFT').gca()
    for i, txt in enumerate(z / (N * T)):
        axes2.annotate(txt, ((z[i]) / (N * T), zy[i]))
    axes2.plot(xf, 2.0 / N * np.abs(yf[0:N // 2]))
    axes2.grid(True, which='both')

    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    demo()
