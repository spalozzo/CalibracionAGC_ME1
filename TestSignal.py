#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 16:10:12 2023

@author: santi
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
from math import floor
import csv

###############################################################################
def writeToCSV(output_file, data0, data1):
    '''
    Funcion para escribir datos a un archivo .csv

    Parameters
    ----------
    output_file : string
        Nombre del archivo a guardar. Si no existe lo crea y si ya existe
        lo sobreescribe.
    data0 : array
        Vector con datos a guardar en la primera columna.
    data1 : array
        Vector con datos a guardar en la segunda columna.

    Returns
    -------
    None.

    '''
    with open(output_file, mode='w', newline='') as archivo_csv:
            escritor_csv = csv.writer(archivo_csv,delimiter=';')
            escritor_csv.writerow(["Tiempo","Amplitud"])
         # Agregar un salto de línea
         
    with open(output_file, mode='a', newline='') as archivo_csv:
        
        escritor_csv = csv.writer(archivo_csv,delimiter=';')
        for col0, col1 in zip(data0, data1):
          escritor_csv.writerow([col0, col1])

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

###############################################################################

plt.close('all')

# Parametros de la señal original
N= 40               # N° de ciclos
frec= 1000          # En [Hz]
cycles= 1/frec      # Periodo de un ciclo
sig_points= 4000    # N° de muestras

# Parametros de la señal modulante
a_max= 10                   # La señal varia entre -a_max y +a_max
div_frec_triangular= 20     # Expresa que tanto mas lenta (o rapida) sera respecto de la señal original

## La idea es que siempre sea mas lenta. Mientras mas lenta es, mas gradual es la variacion de amplitud

test_points= np.linspace(0, N*cycles, sig_points)
amplitudes= a_max * np.abs(sig.sawtooth(2 * np.pi * frec/div_frec_triangular * test_points, 0.5))
''' 
    Sawtooth
    
    El 0.5 indica que la mitad del periodo es ascendente y la otra mitad
    descendente. Esto genera una señal triangular.
    La frecuencia va /10 porque si es mayor, la señal no se modula, y si es
    menor queda cualquier cosa. /10 es el punto justo (hallado empiricamente)
'''
senoidal_pura= np.sin(2 * np.pi * frec * test_points)
test_signal= amplitudes * senoidal_pura


plt.figure()
plt.plot(test_points, amplitudes, label='Señal modulante', linestyle='--')
plt.plot(test_points, senoidal_pura, label='Señal pura', linestyle='--')
plt.plot(test_points, test_signal, label='Señal de prueba')
plt.title('Generación de la Señal de Prueba')
plt.legend()
plt.grid()
plt.show()

writeToCSV("test_signal.csv", test_points, test_signal)

thd_pura= get_THD(senoidal_pura)
thd_modulada= get_THD(test_signal)

print("THD de la señal pura: ",thd_pura)
print("THD de la señal modulada: ",thd_modulada)
