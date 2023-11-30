# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 10:32:17 2023

@author: Santi
"""

# Agregamos el path de las librerias
import sys
sys.path.insert(0, './InstVirtualLib')
import platform

# VISA - Virtual Instrumentation
import pyvisa as visa

# Biblioteca de la Catedra
from InstVirtualLib.osciloscopios import GW_Instek
# from InstVirtualLib.osciloscopios import Tektronix_DSO_DPO_MSO_TDS
import operador

# Generales
import matplotlib.pyplot as plt
from math import floor
import numpy as np
import scipy.signal as sig
import csv

# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)

sys.excepthook = excepthook

def get_THD(test_signal):
    yf = np.fft.fft(test_signal)
    yf = yf[1:floor(len(yf)/2)]
    yf = np.abs(yf) # Obtengo el modulo

    # Calculo el indice donde esta la frecuencia fundamental
    f0_index = np.argmax(yf)

    # Armo vector con los indices de los armonicos
    harmonics__index = np.arange(f0_index,len(yf)-1,f0_index)

    # Creo vector con valores de los harmonicos
    harmonics_values = yf[harmonics__index]

    # Calculo thd
    thd = np.sqrt(np.sum(harmonics_values[1:]**2))/harmonics_values[0]
    
    return thd

plt.close('all')

#%%######################################################################
#############     Conexion del osciloscopio - VISA      #################
#########################################################################

USE_DEVICE = 1

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


#%%######################################################################
###############     Lecturas de prueba - 2 canales      #################
#########################################################################

# Pedimos el trazo de cada canal, la salida es en ([seg.],[volt])
# BUG!!! si no se agrega el VERBOSE=False no anda el GW Instek
print('-------------')
tiempo1, tension1= MiOsciloscopio.get_trace("1",VERBOSE=False)
print('-------------')
tiempo2, tension2= MiOsciloscopio.get_trace("2",VERBOSE=False)
print('-------------')


#%% Plots en subfiguras
test_fig= plt.figure(1)
plt.title('Canales 1 y 2 en subplots')
ax_ch1, ax_ch2= test_fig.subplots(2)

test_fig.sca(ax_ch1)
ax_ch1.plot(tiempo1,tension1, label='Tension canal 1')
plt.legend()
test_fig.sca(ax_ch2)
ax_ch2.plot(tiempo2,tension2, color='red', label='Tension canal 2')
plt.legend()

plt.show()

#%% Plots en la misma figura
plt.figure()
plt.title('Canales 1 y 2 superpuestos')
plt.plot(tiempo1,tension1, label='Tension canal 1')
plt.plot(tiempo2,tension2, color='red', label='Tension canal 2')
plt.legend()
plt.grid()
plt.show()

#%% Plot de la tension diferencial

tension_dif= tension1 - tension2
tension_dif_filtrada= sig.savgol_filter(tension_dif, 4000,50)


plt.figure()
plt.title('Salida Diferencial')
plt.plot(tiempo1,tension_dif, label='Tension Señal Diferencial')
plt.plot(tiempo1,tension_dif_filtrada, label='Tension Señal Diferencial Filtrada')
plt.legend()
plt.grid()
plt.show()

thd_raw= get_THD(tension_dif)
thd_filtrada= get_THD(tension_dif_filtrada)

print("THD de la señal a la salida sin procesar: ",thd_raw)
print("THD de la señal a la salida filtrada: ",thd_filtrada)

#%%######################################################################
#########     Medicion de la señal a la salida del AGC      #############
#########################################################################

tiempo, tension= MiOsciloscopio.get_trace("1",VERBOSE=False)

MiOperador= operador.Operador_osciloscopio(MiOsciloscopio,"Workbench_I")

output_THD = MiOperador.medir_thd(canal = 1, VERBOSE = False)
print('THD = %0.5f'%output_THD)















