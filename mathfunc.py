#!/usr/bin/python3

import wx
import matplotlib as mpl
from matplotlib import figure
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar)
import wx.lib.agw.aui as aui
import numpy as np
from scipy import signal
from scipy.signal import argrelextrema
import math


class Meas:
    def __init__(self, sig):
        self.sig = sig

    def ValMax(self):
        v_max = np.max(self.sig)
        return round(v_max, 5)

    def ValMin(self):
        v_min = np.min(self.sig)
        return round(v_min, 5)

    def ValPeak(self):
        v_peak = abs(self.ValMin()) + abs(self.ValMax())
        return round(v_peak, 5)

    def ValMid(self):
        v_mid = (self.ValMin() + self.ValMax()) / 2
        return round(v_mid, 5)

    def ValAvg(self):
        v_avg = np.average(self.sig)
        return round(v_avg, 5)

    def ValACRMS(self):
        v = 0
        for i in range(len(self.sig)):
            v = v + (self.sig[i] - self.ValAvg()) ** 2
        v = v / len(self.sig)
        v_RMS = np.sqrt(v)
        return round(v_RMS, 5)

    def ValDCRMS(self):
        v = 0
        for i in range(len(self.sig)):
            v = v + (self.sig[i] ** 2)
        v = v / len(self.sig)
        v_RMS = np.sqrt(v)
        return round(v_RMS, 5)

    def ValAmp(self):
        v_amp = (self.ValMax() - self.ValMin()) / 2
        return round(v_amp, 5)

    def ValOver(self):
        v = self.ValAmp()
        if math.isnan(v) or v == 0:
            return 0
        else:
            return round(100 * (self.ValPeak() / v / 2 - 1), 4)

    def PosDuty(self):
        v_sum = sum(i > self.ValMid() for i in self.sig) / len(self.sig)
        return round(v_sum, 4)

    def NegDuty(self):
        v_sum = 1 - self.PosDuty()
        return round(v_sum, 4)


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
    def __init__(self, parent, id=-1):
        super().__init__(parent, id=id)
        self.nb = aui.AuiNotebook(self)
        self.cord = 0
        sizer = wx.BoxSizer()
        pnl = wx.Panel(self)
        sld_pnl = wx.Panel(self)
        stg_pnl = wx.Panel(self)
        meas_pnl = wx.Panel(self)
        chnl_pnl = wx.Panel(self)
        btn_pnl = wx.Panel(self)

        # Tworzenie elementów interfejsu

        # Segment 1. FFT oraz slidery
        self.fftsld = FloatSlider(self, -1, 50, 1, 100, 1)  # slider zmiany szerokości wyszukiwania Hz w FFT
        self.ffttxt = wx.StaticText(sld_pnl, label='50')  # status slidera 1.
        self.fftbtn = wx.Button(sld_pnl, wx.ID_ANY, 'Apply', (10, 10))  # przycisk potwierdzenia szerokości FFT
        self.smplsld = FloatSlider(self, -1, 4096, 4096, 8192, 16)  # slider zmiany wielkości buffora
        self.smpltxt = wx.StaticText(sld_pnl, label='4096')  # status slidera 2.
        self.frqsld = FloatSlider(self, -1, 0, 0, 3, 1)  # slider wyboru symulowanego sygnału
        self.frqtxt = wx.StaticText(sld_pnl, label='1')  # status slidera 3.

        # Segment 2. zmiana podstawy probkowania
        self.btnp1 = wx.Button(stg_pnl, wx.ID_ANY, '+')  # zmiana częstotliwości próbkowania w górę
        self.btnm1 = wx.Button(stg_pnl, wx.ID_ANY, '-')  # zmiana częstotliwości próbkowania w dół
        self.btnat = wx.Button(stg_pnl, wx.ID_ANY, 'Auto')  # automatyczne wyszukiwanie próbek
        self.autoind = wx.StaticText(stg_pnl, label='ON')  # status wyszukiwania automatycznego
        self.smplsts = wx.StaticText(stg_pnl, label='0')  # status próbkowania

        # Segment 3. zarządzanie kanałem 2.
        self.button1 = wx.Button(btn_pnl, wx.ID_ANY, 'Run', (10, 10))  # uruchomienie nowego pomiaru
        self.button2 = wx.Button(btn_pnl, wx.ID_ANY, 'CH2 Enable')  # włączenie pomiarów dla drugiego kanału
        self.btnsts = wx.StaticText(btn_pnl, label='0')  # status kanału 2.

        # slider do zmiany cz. próbkowania
        # self.persld = FloatSlider(self, -1, 0, 0, 7, 1)                 # slider wyboru szybkości próbkowania
        # self.pertxt = wx.StaticText(sld_pnl, label='1')                 # status slidera 4.

        # Segment 3. parametry sygnału
        self.vmin = wx.StaticText(meas_pnl, label='1')  # napięcie minimalne
        self.vmax = wx.StaticText(meas_pnl, label='1')  # napięcie maksymalne
        self.vpeak = wx.StaticText(meas_pnl, label='1')  # napięcie p2p
        self.vmid = wx.StaticText(meas_pnl, label='1')  # napięcie środkowe
        self.vavg = wx.StaticText(meas_pnl, label='1')  # napięcie średnie
        self.vacrms = wx.StaticText(meas_pnl, label='1')  # napięcie skuteczne zmienne
        self.vdcrms = wx.StaticText(meas_pnl, label='1')  # napięcie skuteczne stałe
        self.vamp = wx.StaticText(meas_pnl, label='1')  # amplituda napięcia
        self.vover = wx.StaticText(meas_pnl, label='0')  # napięcie przebijające
        self.vpduty = wx.StaticText(meas_pnl, label='0 %')  # wypełnienia dodatnie
        self.vnduty = wx.StaticText(meas_pnl, label='0 %')  # wypełnienie ujemne
        self.freq = wx.StaticText(meas_pnl, label='0 Hz')  # częstotliwość sygnału

        # Segment 4. wybór kanału do pomiaru
        self.chnlid = wx.StaticText(chnl_pnl, label='CH1')  # aktualnie mierzony sygnał
        self.btnch1 = wx.Button(chnl_pnl, wx.ID_ANY, 'CH1')  # przyciski odczytania parametrów sygnałów
        self.btnch2 = wx.Button(chnl_pnl, wx.ID_ANY, 'CH2')  # dla 1. i 2. kanału

        # Deklaracja układu elementów
        sld_sizer = wx.GridBagSizer(1, 1)
        stg_sizer = wx.GridBagSizer(1, 1)
        meas_sizer = wx.GridBagSizer(1, 2)
        pnl_sizer = wx.GridBagSizer(1, 1)
        chnl_sizer = wx.GridBagSizer(1, 1)
        btn_sizer = wx.GridBagSizer(1, 1)


        # Rozmieszczanie elementów w danych panelach

        # Segment 1. FFT oraz slidery
        sld_sizer.Add(wx.StaticText(sld_pnl, label='FFT'), pos=(0, 0), flag=wx.LEFT, border=10)
        sld_sizer.Add(self.fftsld, pos=(1, 0), flag=wx.ALL | wx.EXPAND, border=1)
        sld_sizer.Add(self.ffttxt, pos=(1, 1), flag=wx.RIGHT, border=10)
        sld_sizer.Add(self.fftbtn, pos=(2, 0), flag=wx.ALL | wx.EXPAND, border=1)
        sld_sizer.Add(wx.StaticText(sld_pnl, label='N samples'), pos=(3, 0), flag=wx.LEFT, border=10)
        sld_sizer.Add(self.smplsld, pos=(4, 0), flag=wx.ALL | wx.EXPAND, border=1)
        sld_sizer.Add(self.smpltxt, pos=(4, 1), flag=wx.RIGHT, border=10)
        sld_sizer.Add(wx.StaticText(sld_pnl, label='FRQ'), pos=(5, 0), flag=wx.LEFT, border=10)
        sld_sizer.Add(self.frqsld, pos=(6, 0), flag=wx.ALL | wx.EXPAND, border=1)
        sld_sizer.Add(self.frqtxt, pos=(6, 1), flag=wx.RIGHT, border=10)

        # Segment 2. rozmieszczenie
        stg_sizer.Add(wx.StaticText(stg_pnl, label='Auto Fq search'), pos=(0, 0), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=10)
        stg_sizer.Add(self.btnat, pos=(1, 0), flag=wx.ALL | wx.EXPAND, border=10)
        stg_sizer.Add(self.autoind, pos=(1, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=10)
        stg_sizer.Add(wx.StaticText(stg_pnl, label='Fp'), pos=(2, 0), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=10)
        stg_sizer.Add(self.btnp1, pos=(3, 0), flag=wx.ALL | wx.EXPAND, border=10)
        stg_sizer.Add(self.smplsts, pos=(3, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=20)
        stg_sizer.Add(self.btnm1, pos=(3, 2), flag=wx.ALL | wx.EXPAND, border=10)

        # Segment 3. rozmieszczenie
        btn_sizer.Add(self.button1, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=1)
        btn_sizer.Add(self.btnsts, pos=(1, 1), flag=wx.CENTER, border=10)
        btn_sizer.Add(self.button2, pos=(1, 0), flag=wx.ALL | wx.EXPAND, border=1)


        # Segment 4. rozmieszczenie
        meas_sizer.Add(wx.StaticText(meas_pnl, label='Maximum'), pos=(0, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='Minimum'), pos=(1, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='Peak2Peak'), pos=(2, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='Middle'), pos=(3, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='Average'), pos=(4, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='AC RMS'), pos=(5, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='DC RMS'), pos=(6, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='Amplitude'), pos=(7, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='Overshoot'), pos=(8, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='Pos Duty'), pos=(9, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='Neg Duty'), pos=(10, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(wx.StaticText(meas_pnl, label='Freq'), pos=(11, 0), flag=wx.LEFT, border=10)
        meas_sizer.Add(self.vmax, pos=(0, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.vmin, pos=(1, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.vpeak, pos=(2, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.vmid, pos=(3, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.vavg, pos=(4, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.vacrms, pos=(5, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.vdcrms, pos=(6, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.vamp, pos=(7, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.vover, pos=(8, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.vpduty, pos=(9, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.vnduty, pos=(10, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(self.freq, pos=(11, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=1)
        meas_sizer.Add(wx.StaticText(meas_pnl, label=''), pos=(0, 2), flag=wx.RIGHT, border=100)

        # Segment 5. rozmieszczenie
        chnl_sizer.Add(self.btnch1, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=10)
        chnl_sizer.Add(self.chnlid, pos=(0, 1), flag=wx.ALL | wx.EXPAND | wx.CENTER, border=20)
        chnl_sizer.Add(self.btnch2, pos=(0, 2), flag=wx.ALL | wx.EXPAND, border=10)

        # testowe elementy
        # pnl_sizer.Add(wx.StaticText(pnl, label='ST'), pos=(7, 0), flag=wx.LEFT, border=10)
        # pnl_sizer.Add(self.txt3, pos=(8, 1), flag=wx.RIGHT, border=10)
        # pnl_sizer.Add(self.fslider3, pos=(8, 0), flag=wx.ALL | wx.EXPAND, border=1)

        # inicializacja paneli
        sld_sizer.AddGrowableCol(0)
        sld_sizer.SetMinSize(200, 100)
        sld_pnl.SetSizer(sld_sizer)

        stg_sizer.AddGrowableCol(0)
        stg_sizer.SetMinSize(200, 100)
        stg_pnl.SetSizer(stg_sizer)

        btn_sizer.AddGrowableCol(0)
        btn_sizer.SetMinSize(200, 100)
        btn_pnl.SetSizer(btn_sizer)

        meas_sizer.AddGrowableCol(0)
        meas_sizer.SetMinSize(200, 100)
        meas_pnl.SetSizer(meas_sizer)

        chnl_sizer.AddGrowableCol(0)
        chnl_sizer.SetMinSize(200, 100)
        chnl_pnl.SetSizer(chnl_sizer)

        pnl_sizer.Add(sld_pnl, pos=(0, 0), flag=wx.ALL | wx.EXPAND)
        pnl_sizer.Add(stg_pnl, pos=(1, 0), flag=wx.ALL | wx.EXPAND)
        pnl_sizer.Add(btn_pnl, pos=(2, 0), flag=wx.ALL | wx.EXPAND)
        pnl_sizer.Add(meas_pnl, pos=(3, 0), flag=wx.ALL | wx.EXPAND)
        pnl_sizer.Add(chnl_pnl, pos=(4, 0), flag=wx.ALL | wx.EXPAND)

        pnl_sizer.AddGrowableCol(0)
        pnl_sizer.SetMinSize(200, 100)
        pnl.SetSizer(pnl_sizer)
        sizer.Add(pnl, 0, wx.SHAPED)

        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def RefVal(self, event):
        self.ffttxt.SetLabel(str(self.fftsld.GetValue()))
        self.smpltxt.SetLabel(str(self.smplsld.GetValue()))
        self.frqtxt.SetLabel(str(self.frqsld.GetValue()))
        # self.txt3.SetLabel(str(self.fslider3.GetValue()))
        self.fftsld.Bind(wx.EVT_SCROLL, self.fftsld._OnScroll)
        self.smplsld.Bind(wx.EVT_SCROLL, self.smplsld._OnScroll)
        self.frqsld.Bind(wx.EVT_SCROLL, self.frqsld._OnScroll)
        # self.fslider3.Bind(wx.EVT_SCROLL, self.fslider3._OnScroll)

    def add(self, name="plot"):
        page = Plot(self.nb)
        self.nb.AddPage(page, name)
        return page.figure

    def delI(self, id):
        self.nb.DeletePage(id)


def switch_demo(argument, hz, am, st, x):
    y = {
        1: am * np.sin(hz * 2.0 * np.pi * x) - st,
        2: am * signal.square(hz * 2.0 * np.pi * x, duty=0.5) - st,
        3: am * signal.sawtooth(hz * 2.0 * np.pi * x) - st
    }
    return y.get(argument)


class FFT_Func:
    def __init__(self, y, N, T, res):
        self.y = y
        self.N = N
        self.T = T
        self.res = res

    def FFT_Y(self):
        yf = np.fft.fft(self.y)
        return yf

    def FFT_X(self):
        xf = np.fft.fftfreq(self.N, self.T)[:self.N // 2]
        return xf

    def FFT_Freq(self):
        z = argrelextrema(2.0 / self.N * np.abs(self.FFT_Y()[0:self.N // 2]), np.greater, 0, self.res)
        z = np.concatenate(np.asarray(z))
        return z

    def FFT_Freq_Y(self):
        zy = np.ones(len(self.FFT_Freq())) * (2.0 / self.N * np.abs(self.FFT_Y()[self.FFT_Freq()]))
        # s = np.zeros(len(z))
        return zy


def period(freq):
    y = {
        0: 1 / 100000,
        1: 1 / 10000,
        2: 1 / 5000,
        3: 1 / 1000,
        4: 1 / 500,
        5: 1 / 1000,
        6: 1 / 500,
        7: 1 / 10000
    }
    return y.get(freq)
