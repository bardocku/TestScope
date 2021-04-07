#!/usr/bin/env python3

import wx
import numpy as np
import scipy as sp
from matplotlib.pyplot import minorticks_on
from mathfunc import (Meas, PlotNotebook, Plot, FloatSlider, switch_demo, FFT_Func)


# Number of sample points
N = 2000
# sample spacing
T = 1.0 / 1000.0
x = np.linspace(0.0, N * T, N, endpoint=False)


def demo():
    app = wx.App()
    frame = wx.Frame(None, -1, 'Plotter')
    plotter = PlotNotebook(frame)
    btn = 0

    sd0 = plotter.fslider0.GetValue()
    sd1 = plotter.fslider1.GetValue()
    sd2 = plotter.fslider2.GetValue()
    sd3 = plotter.fslider3.GetValue()
    y1 = switch_demo(2, 10, 2, 0, x)
    y = switch_demo(sd3, sd2, sd1, sd3, x)
    fft_ch = FFT_Func(y, N, T, sd0)

    def ValAct(sig):
        y_meas = Meas(sig)
        fft_ch = FFT_Func(sig, N, T/500, sd0)
        max_v = np.argmax(fft_ch.FFT_Freq_Y())
        max_f = (fft_ch.FFT_Freq()[max_v]) / (N * T)
        duty = y_meas.PosDuty()
        plotter.vpeak.SetLabel(str(y_meas.ValPeak()) + ' V')
        plotter.vmax.SetLabel(str(y_meas.ValMax()) + ' V')
        plotter.vmin.SetLabel(str(y_meas.ValMin()) + ' V')
        plotter.vmid.SetLabel(str(y_meas.ValMid()) + ' V')
        plotter.vavg.SetLabel(str(y_meas.ValAvg()) + ' V')
        plotter.vacrms.SetLabel(str(y_meas.ValACRMS()) + ' Ṽ')
        plotter.vdcrms.SetLabel(str(y_meas.ValDCRMS()) + ' Ṽ')
        plotter.vamp.SetLabel(str(y_meas.ValAmp()) + ' V')
        plotter.vover.SetLabel((str(y_meas.ValOver()) + ' %'))
        plotter.vpduty.SetLabel(str(duty) + ' %')
        plotter.vnduty.SetLabel(str(round(1 - duty, 4)) + ' %')
        plotter.freq.SetLabel(str(max_f) + ' Hz')

    ValAct(y)

    axes1 = plotter.add('Signal').gca()
    ax1 = 0
    axes1.plot(x, y)
    axes1.minorticks_on()
    axes1.grid(True, which='both')

    axe2 = plotter.add('FFT').gca()
    ax2 = 1
    for i, txt in enumerate(fft_ch.FFT_Freq() / (N * T)):
        axe2.annotate(txt, ((fft_ch.FFT_Freq()[i]) / (N * T), fft_ch.FFT_Freq_Y()[i]))
    axe2.plot(fft_ch.FFT_X(), 2.0 / N * np.abs(fft_ch.FFT_Y()[0:N // 2]))
    axe2.minorticks_on()
    axe2.grid(True, which='both')

    def onButton1(event):
        sd0 = plotter.fslider0.GetValue()
        sd1 = plotter.fslider1.GetValue()
        sd2 = plotter.fslider2.GetValue()
        sd3 = plotter.fslider3.GetValue()

        nonlocal ax1
        nonlocal ax2
        nonlocal y

        y1 = switch_demo(2, 10, 2, 0, x)
        y = switch_demo(sd3, sd2, sd1, sd3, x)
        ValAct(y)

        plotter.delI(ax1)
        ax2 = 0
        ax1 = 1

        axe = plotter.add('Signal').gca()
        axe.plot(x, y)
        if btn == 1:
            axe.plot(x, y1)
        axe.minorticks_on()
        axe.grid(True, which='both', axis='both')

    def onButton0(event):
        sd0 = plotter.fslider0.GetValue()
        sd1 = plotter.fslider1.GetValue()
        sd2 = plotter.fslider2.GetValue()
        sd3 = plotter.fslider3.GetValue()

        nonlocal ax2
        nonlocal ax1
        nonlocal y
        y = switch_demo(sd3, sd2, sd1, sd3, x)
        fft_ch = FFT_Func(y, N, T, sd0)


        plotter.delI(ax2)
        ax1 = 0
        ax2 = 1
        axe2 = plotter.add('FFT').gca()
        for i, txt in enumerate(fft_ch.FFT_Freq() / (N * T)):
            axe2.annotate(txt, ((fft_ch.FFT_Freq()[i]) / (N * T), fft_ch.FFT_Freq_Y()[i]))
        axe2.plot(fft_ch.FFT_X(), 2.0 / N * np.abs(fft_ch.FFT_Y()[0:N // 2]))
        axe2.minorticks_on()
        axe2.grid(True, which='both', axis='both')

    def onButton2(event):
        nonlocal btn
        btn ^= 1
        plotter.txt4.SetLabel(str(btn))

    def ChngChnl1(event):
        ValAct(y)
        plotter.chnlid.SetLabel(str('CH1'))

    def ChngChnl2(event):
        ValAct(y1)
        plotter.chnlid.SetLabel(str('CH2'))

    plotter.button.Bind(wx.EVT_BUTTON, onButton0)
    plotter.button1.Bind(wx.EVT_BUTTON, onButton1)
    plotter.button2.Bind(wx.EVT_BUTTON, onButton2)
    plotter.btnch1.Bind(wx.EVT_BUTTON, ChngChnl1)
    plotter.btnch2.Bind(wx.EVT_BUTTON, ChngChnl2)
    plotter.fslider0.Bind(wx.EVT_SCROLL, plotter.RefVal)
    plotter.fslider1.Bind(wx.EVT_SCROLL, plotter.RefVal)
    plotter.fslider2.Bind(wx.EVT_SCROLL, plotter.RefVal)
    plotter.fslider3.Bind(wx.EVT_SCROLL, plotter.RefVal)

    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    demo()
