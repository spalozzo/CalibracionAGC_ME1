# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 10:32:17 2023

@author: Santi
"""

# Agregamos el path de las librerias
import sys
sys.path.insert(0, 'InstVirtualLib')
import platform

# VISA - Virtual Instrumentation
import pyvisa as visa

# Biblioteca de la Catedra
from InstVirtualLib.osciloscopios import GW_Instek
# from InstVirtualLib.osciloscopios import Tektronix_DSO_DPO_MSO_TDS
import operador

# Generales
import matplotlib.pyplot as plt
import numpy as np
import csv

# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)

sys.excepthook = excepthook

plt.close('all')

USE_DEVICE = 0

# Abrimos el instrumento
platforma = platform.platform()
print(platforma)
rm=visa.ResourceManager()

# El handle puede controlar osciloscopios, analizadores, etc.
# Es generico
instrument_handler=rm.open_resource(rm.list_resources()[USE_DEVICE])

# Creo el Osciloscopio
MiOsciloscopio = GW_Instek(instrument_handler)

# Informamos el modelo del osciloscopio conectado
print("Esta conectado un %s"%MiOsciloscopio.INSTR_ID)


# Pedimos el trazo de cada canal, la salida es en ([seg.],[volt])
# BUG!!! si no se agrega el VERBOSE=False no anda el GW Instek
print('-------------')
tiempo1, tension1= MiOsciloscopio.get_trace("1",VERBOSE=False)
print('-------------')
tiempo2, tension2= MiOsciloscopio.get_trace("2",VERBOSE=False)
print('-------------')

# Ploteamos los canales
test_fig= plt.figure(1)
ax_ch1, ax_ch2= test_fig.subplots(2)

test_fig.sca(ax_ch1)
ax_ch1.plot(tiempo1,tension1, label='Tension canal 1')
plt.legend()
test_fig.sca(ax_ch2)
ax_ch2.plot(tiempo2,tension2, color='red', label='Tension canal 2')
plt.legend()

plt.show()

# Genero la señal de prueba
N= 15
frec= 1000 # 1kHz
cycles= 1/frec
sig_points= 4000

# Amplitudes
low_value= 1
top_value= 10

ascending=  np.linspace(low_value, top_value, int(sig_points/2))
descending= np.linspace(top_value, low_value, int(sig_points/2))
amplitudes= np.append(ascending, descending)


test_points= np.linspace(0, N*cycles, sig_points)
test_signal= amplitudes * np.sin(2 * np.pi * frec * test_points)

plt.figure()
plt.plot(test_points, test_signal, label='Señal de prueba')
plt.legend()
plt.grid()
plt.show()

# Medicion de la señal a la salida del AGC
tiempo, tension= MiOsciloscopio.get_trace("1",VERBOSE=False)

MiOperador= operador.Operador_osciloscopio(MiOsciloscopio,"Workbench_I")

output_THD = MiOperador.medir_thd(canal = 1, VERBOSE = False)
print('THD = %0.5f'%output_THD)















