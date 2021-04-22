#!/usr/bin/python3

# Inicjalizacja bibliotek
import wx
import numpy as np
import scipy as sp
from matplotlib.pyplot import minorticks_on
from mathfunc import (Meas, PlotNotebook, Plot, FloatSlider, switch_demo, FFT_Func, period)
from pynq import Overlay
import pynq
from pynq import MMIO
import time
from IPython.display import clear_output

# Zaprogramownie układu logiki
ol = Overlay("/home/xilinx/jupyter_notebooks/HW/Test_HW3/sensors96b.bit") # Tcl is parsed here

# gpio_w = ol.axi_gpio_0.channel2
# gpio_r = ol.axi_gpio_0.channel1

# Definicja adresów pamięci przypisanych do portów AXI GPIO
IP_BASE_ADDRESS = 0x80000000
ADDRESS_RANGE = 0xFFFF
ADDRESS_OFFSET = 0x08;
ADDRESS_OFFSET1 = 0x00;

# Stowrzenie obiektu
mmio = MMIO(IP_BASE_ADDRESS, ADDRESS_RANGE)

# Definicja metody odzczytu i zapisu na portch GPIO
def write_gpio(data):
    return mmio.write(ADDRESS_OFFSET, data)

def read_gpio(addr):
    return mmio.read(addr)

# Funkcja programu okienkowego
def demo():
    # Inicjalizacja obiektu okna programu
    app = wx.App()
    frame = wx.Frame(None, -1, 'Plotter')
    plotter = PlotNotebook(frame)
    
    # Deklaracja zmiennych
    btn = 0
    vbuf = 0
    vsig = 0
    
    # Włączenie modułu testowego sinusa
    write_gpio(0b00000000)
    write_gpio(0b11110111)
    
    # Odczyt stanów slidera
    sd0 = plotter.fslider0.GetValue()
    N = plotter.fslider1.GetValue()
    sd2 = plotter.fslider2.GetValue()
    sd3 = plotter.fslider3.GetValue()
    
    # Odstęp próbek
    T = period(sd3)
    print(N)
    # Deklaracja metody zmiany 
    def ChgSig(sd3,sd2):
	    nonlocal vbuf
	    nonlocal vsig
	    vbuf = 0
	    vsig = 0
	    vbuf = sd3<<3
	    vsig = sd2<<1
	    vsig = vsig|0b1|vbuf|0b01000000
	    write_gpio(vsig)
	    print(vsig)

	# Inicjalizacja tablic
    yx = np.zeros(N)
    yz = np.zeros(N)
    buffor = np.zeros(N)

	# Deklaracja metod inicjalizacji szerokości bufora i zapisu próbek
    def memory(N):
        nonlocal buffor
        buffor = pynq.allocate(shape=(N,), dtype=np.uint8)
        ol.fun_0.s_axi_mem_ptr.register_map.out_data_p_1 = buffor.physical_address
        ol.fun_0.s_axi_buf_size.register_map.buffsize = N
        ol.fun_0.s_axi_read_flag.register_map.rd = 0

    def readMemory():
         nonlocal yx
         ol.fun_0.s_axi_read_flag.register_map.rd = 1
         ol.fun_0.s_axi_read_flag.register_map.rd = 0
         yx=np.frombuffer(buffor, dtype=np.uint8)
         yx = yx/255

	# Inicjalizacja szerkości próbek
    memory(N)

    time.sleep(1)
    # sample spacing
    x = np.linspace(0.0, N * T, N, endpoint=False)
    time.sleep(1)
    readMemory()
	
	# Przekazanie danych do funkcji FFT
    
    # fft_ch = FFT_Func(yx, N, T, sd0)
    
    # Metoda aktualizacji pramatrów sygnału
    def ValAct(sig):
        y_meas = Meas(sig)
        fft_ch = FFT_Func(sig, N, T, 1)
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
    
    
    # ValAct(yx)
	
	# Tworzenie krat z wykresami
    axes1 = plotter.add('Signal').gca()
    ax1 = 0
    axes1.plot(x,yx)
    axes1.minorticks_on()
    axes1.grid(True, which='both')

    axe2 = plotter.add('FFT').gca()
    ax2 = 1
    # for i, txt in enumerate(fft_ch.FFT_Freq() / (N * T)):
    #     axe2.annotate(txt, ((fft_ch.FFT_Freq()[i]) / (N * T), fft_ch.FFT_Freq_Y()[i]))
    # axe2.plot(fft_ch.FFT_X(), 2.0 / N * np.abs(fft_ch.FFT_Y()[0:N // 2]))
    # axe2.minorticks_on()
    # axe2.grid(True, which='both')

    # Metoda obsługi przycisku aktualizacji ustawień bufora
    def onButton1(event):
        nonlocal ax2
        nonlocal ax1
        nonlocal N
        nonlocal x
        nonlocal yz
        nonlocal yx
        nonlocal T
        sd0 = plotter.fslider0.GetValue()
        N = plotter.fslider1.GetValue()
        sd2 = plotter.fslider2.GetValue()
        sd3 = plotter.fslider3.GetValue()
        T = period(sd3)
        ChgSig(sd3,sd2)
        memory(N)
        time.sleep(1)       
        x = np.linspace(0.0, N * T, N, endpoint=False)
        
        # Włączenie drugiego kanału
        # if btn == 1:
        
        readMemory()
        time.sleep(1)
        ValAct(yx)

        plotter.delI(ax1)
        ax2 = 0
        ax1 = 1
        axe = plotter.add('Signal').gca()
        axe.plot(x, yx)
        if btn == 1:
            axe.plot(x, yz)
        axe.minorticks_on()
        axe.grid(True, which='both', axis='both')

    def onButton0(event):
        nonlocal ax2
        nonlocal ax1
        nonlocal N
        nonlocal x
        
        sd0 = plotter.fslider0.GetValue()
        N = plotter.fslider1.GetValue()
        sd2 = plotter.fslider2.GetValue()
        sd3 = plotter.fslider3.GetValue()

        fft_ch = FFT_Func(yx, N, T, sd0)

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
        ValAct(yx)
        plotter.chnlid.SetLabel(str('CH1'))

    def ChngChnl2(event):
        if btn == 1:
            ValAct(yz)
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
