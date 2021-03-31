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


def switch_demo(argument, hz, am, st):
    y = {
        1: am * np.sin(hz * 2.0 * np.pi * x) + st,
        2: am * signal.square(hz * 2.0 * np.pi * x) + st,
        3: am * signal.sawtooth(1.0 * 2.0 * np.pi * x) + st
    }
    return y.get(argument)


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


class Plot(wx.Panel):

    def __init__(self, parent, id=-1, dpi=None, **kwargs):
        super().__init__(parent, id=id, **kwargs)
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2, 2))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.Centre()
        self.SetSizer(sizer)


class PlotNotebook(wx.Panel):
    idzed = 0
    def __init__(self, parent, id=-1):
        super().__init__(parent, id=id)
        self.nb = aui.AuiNotebook(self)
        sizer = wx.BoxSizer()
        pnl = wx.Panel(self)

        self.button = wx.Button(self, wx.ID_ANY, 'Apply', (10, 10))
        # self.button.Bind(wx.EVT_BUTTON, onButton)

        self.button1 = wx.Button(self, wx.ID_ANY, 'Change signal', (10, 10))
        # self.button.Bind(wx.EVT_BUTTON, onButton)

        self.fslider0 = FloatSlider(self, -1, 1, 1, 100, 1)
        self.fslider1 = FloatSlider(self, -1, 1, 1, 100, 1)
        self.fslider2 = FloatSlider(self, -1, 1, 1, 100, 1)
        self.fslider3 = FloatSlider(self, -1, 1, 1, 3, 1)
        self.txt0 = wx.StaticText(pnl, label='1')
        self.txt1 = wx.StaticText(pnl, label='1')
        self.txt2 = wx.StaticText(pnl, label='1')
        self.txt3 = wx.StaticText(pnl, label='1')
        pnl_sizer = wx.GridBagSizer(1, 1)
        pnl_sizer.Add(wx.StaticText(pnl, label='FFT'), pos=(0, 0), flag=wx.LEFT, border=10)
        pnl_sizer.Add(wx.StaticText(pnl, label='AMP'), pos=(3, 0), flag=wx.LEFT, border=10)
        pnl_sizer.Add(wx.StaticText(pnl, label='FRQ'), pos=(5, 0), flag=wx.LEFT, border=10)
        pnl_sizer.Add(wx.StaticText(pnl, label='ST'), pos=(7, 0), flag=wx.LEFT, border=10)
        pnl_sizer.Add(self.txt0, pos=(1, 1), flag=wx.RIGHT, border=10)
        pnl_sizer.Add(self.txt1, pos=(4, 1), flag=wx.RIGHT, border=10)
        pnl_sizer.Add(self.txt2, pos=(6, 1), flag=wx.RIGHT, border=10)
        pnl_sizer.Add(self.txt3, pos=(8, 1), flag=wx.RIGHT, border=10)
        pnl_sizer.Add(self.fslider0, pos=(1, 0), flag=wx.ALL | wx.EXPAND, border=1)
        pnl_sizer.Add(self.fslider1, pos=(4, 0), flag=wx.ALL | wx.EXPAND, border=1)
        pnl_sizer.Add(self.fslider2, pos=(6, 0), flag=wx.ALL | wx.EXPAND, border=1)
        pnl_sizer.Add(self.fslider3, pos=(8, 0), flag=wx.ALL | wx.EXPAND, border=1)
        pnl_sizer.Add(self.button, pos=(2, 0), flag=wx.ALL | wx.EXPAND, border=1)
        pnl_sizer.Add(self.button1, pos=(9, 0), flag=wx.ALL | wx.EXPAND, border=1)
        pnl_sizer.AddGrowableCol(0)
        pnl_sizer.SetMinSize(200, 100)
        pnl.SetSizer(pnl_sizer)
        sizer.Add(pnl, 0, wx.SHAPED)
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def RefVal(self, event):
        self.txt0.SetLabel(str(self.fslider0.GetValue()))
        self.txt1.SetLabel(str(self.fslider1.GetValue()))
        self.txt2.SetLabel(str(self.fslider2.GetValue()))
        self.txt3.SetLabel(str(self.fslider3.GetValue()))
        self.fslider0.Bind(wx.EVT_SCROLL, self.fslider0._OnScroll)
        self.fslider1.Bind(wx.EVT_SCROLL, self.fslider1._OnScroll)
        self.fslider2.Bind(wx.EVT_SCROLL, self.fslider2._OnScroll)
        self.fslider3.Bind(wx.EVT_SCROLL, self.fslider3._OnScroll)

    def add(self, name="plot"):
        page = Plot(self.nb)
        self.nb.AddPage(page, name)
        return page.figure

    def delI(self, id):
        self.nb.DeletePage(id)


# Number of sample points
N = 5000
# sample spacing
T = 1.0 / 800.0
x = np.linspace(0.0, N * T, N, endpoint=False)


def demo():
    app = wx.App()
    frame = wx.Frame(None, -1, 'Plotter')
    plotter = PlotNotebook(frame)

    P0=0
    P1=0

    sd0 = plotter.fslider0.GetValue()
    sd1 = plotter.fslider1.GetValue()
    sd2 = plotter.fslider2.GetValue()
    sd3 = plotter.fslider3.GetValue()

    y = switch_demo(sd3, sd2, sd1, sd3)
    yf = np.fft.fft(y)
    xf = np.fft.fftfreq(N, T)[:N // 2]

    res = max(20 / N * np.abs(yf[0:N // 2]))
    z = argrelextrema(2.0 / N * np.abs(yf[0:N // 2]), np.greater, 0, sd0)
    z = np.concatenate(np.asarray(z))
    zy = np.ones(len(z)) * (2.0 / N * np.abs(yf[z]))
    s = np.zeros(len(z))

    axes1 = plotter.add('Signal').gca()
    ax1 = 0
    p1 = 0
    print(plotter.idzed)
    axes1.plot(x, y)
    axes1.plot(x, -y)
    axes1.plot(x + 0.1, y - 0.5 * y)
    axes1.grid(True, which='both')

    axes2 = plotter.add('FFT').gca()
    ax2 = 1
    print(plotter.idzed)
    for i, txt in enumerate(z / (N * T)):
        axes2.annotate(txt, ((z[i]) / (N * T), zy[i]))
    axes2.plot(xf, 2.0 / N * np.abs(yf[0:N // 2]))
    axes2.grid(True, which='both')

    def onButton1(event):
        sd0 = plotter.fslider0.GetValue()
        sd1 = plotter.fslider1.GetValue()
        sd2 = plotter.fslider2.GetValue()
        sd3 = plotter.fslider3.GetValue()

        y = switch_demo(sd3, sd2, sd1, sd3)
        yf = np.fft.fft(y)
        xf = np.fft.fftfreq(N, T)[:N // 2]

        res = max(20 / N * np.abs(yf[0:N // 2]))
        z = argrelextrema(2.0 / N * np.abs(yf[0:N // 2]), np.greater, 0, sd0)
        z = np.concatenate(np.asarray(z))
        zy = np.ones(len(z)) * (2.0 / N * np.abs(yf[z]))
        s = np.zeros(len(z))
        nonlocal ax1
        nonlocal ax2
        nonlocal P0


        plotter.delI(ax1)
        ax2 = 0
        ax1 = 1

        axe = plotter.add('Signal').gca()
        axe.plot(x, y)
        axe.plot(x, -y)
        axe.plot(x + 0.1, y - 0.5 * y)
        axe.grid(True, which='both')

    def onButton0(event):
        sd0 = plotter.fslider0.GetValue()
        sd1 = plotter.fslider1.GetValue()
        sd2 = plotter.fslider2.GetValue()
        sd3 = plotter.fslider3.GetValue()

        y = switch_demo(sd3, sd2, sd1, sd3)
        yf = np.fft.fft(y)
        xf = np.fft.fftfreq(N, T)[:N // 2]

        res = max(20 / N * np.abs(yf[0:N // 2]))
        z = argrelextrema(2.0 / N * np.abs(yf[0:N // 2]), np.greater, 0, sd0)
        z = np.concatenate(np.asarray(z))
        zy = np.ones(len(z)) * (2.0 / N * np.abs(yf[z]))
        s = np.zeros(len(z))

        nonlocal ax2
        nonlocal ax1
        nonlocal P1


        plotter.delI(ax2)
        ax1 = 0
        ax2 = 1
        axe2 = plotter.add('FFT').gca()
        for i, txt in enumerate(z / (N * T)):
            axe2.annotate(txt, ((z[i]) / (N * T), zy[i]))
        axe2.plot(xf, 2.0 / N * np.abs(yf[0:N // 2]))
        axe2.grid(True, which='both')

    plotter.button.Bind(wx.EVT_BUTTON, onButton0)
    plotter.button1.Bind(wx.EVT_BUTTON, onButton1)
    plotter.fslider0.Bind(wx.EVT_SCROLL, plotter.RefVal)
    plotter.fslider1.Bind(wx.EVT_SCROLL, plotter.RefVal)
    plotter.fslider2.Bind(wx.EVT_SCROLL, plotter.RefVal)
    plotter.fslider3.Bind(wx.EVT_SCROLL, plotter.RefVal)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    demo()
