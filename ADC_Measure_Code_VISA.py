# sudo apt-get install python3-serial
import serial
# pip3 install numpy
import numpy as np

from time import time, sleep

import matplotlib.pyplot as plt

# Traemos la libreria VISA
import pyvisa as visa
# Traemos matplotlib para poder graficar
import matplotlib.pyplot as plt
# Agreamos el path de las librerias
import sys
sys.path.insert(0, './InstVirtualLib')
import platform
# Traemos el generador
from InstVirtualLib.generadores_arbitrarios import Agilent33512A
from InstVirtualLib.generadores_arbitrarios import RigolDG5071

# Siempre util numpy y scipy...
import numpy as np
from scipy import signal
import csv

archivo_salida = "registro_cuarto_de_LSB.csv"

def escribir_en_csv(gen,vector):
   
     with open(archivo_salida, mode='a', newline='') as archivo_csv:
         
         escritor_csv = csv.writer(archivo_csv,delimiter=';')
         for this_value in vector:
           escritor_csv.writerow([gen,this_value])

         # Agregar un salto de línea
       
with open(archivo_salida, mode='w', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv,delimiter=';')
        escritor_csv.writerow(["vGen","Cuenta"])
     # Agregar un salto de línea



PUERTO = '/dev/ttyUSB0'
BAUD_RATE = 9600
TIMEOUT = 0.5

N_BITS = 10
VCC = 10
CANT_POR_CUENTA= 4

NUM_MEDICIONES = (2**N_BITS) * CANT_POR_CUENTA
NUM_ADQUISICIONES = 5

'''
VCC es la tension maxima de alimentacion que soporta el ADC. NBITS es
el n° de bits del ADC y CANT_POR_CUENTA es la cantidad de mediciones 
que quiero hacer en una misma cuenta.
Por ejemplo, si es igual a 2, le estoy pidiendo que mida en 0LSB, 1/2LSB
1LSB, 3/2LSB, etc. Por cada cuenta mido en 0 y 1/2 mas adelante.
'''

WAIT_MS = 100

# Variables no usadas
# CUENTAS = ((2**N_BITS)-1)
# K_teorica = VCC / CUENTAS


def get_count(port):
    while True:
        try:
            # Pido una muestra
            port.write('M'.encode())
            # La leo
            entrada = port.readline()
            # La convierto y la retorno
            return int(entrada[:-2])
        except:
            print('.')
            

port = serial.Serial(PUERTO,
        baudrate = BAUD_RATE,
        timeout = TIMEOUT)


# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)

sys.excepthook = excepthook

# Device a utilizar de la lista
USE_DEVICE = 1

# Abrimos el instrumento con el backend correcto
platforma = platform.platform()
print(platforma)
rm=visa.ResourceManager()

# Instancio el instrumento
instrument_handler=rm.open_resource(rm.list_resources()[USE_DEVICE])
MiGenArb = Agilent33512A(instrument_handler)

# Informamos el modelo del generador conectado
print("Esta conectado un %s"%MiGenArb.INSTR_ID)



sleep(2)

# MiGenArb.continua(10)

matriz_medicion = np.zeros((NUM_MEDICIONES,NUM_ADQUISICIONES))

# Vector con los valores de tension a mandar al generador.
# Regula el paso de las mediciones que vamos a hacer, definido
# por NUM_MEDICIONES
v_val_list = np.linspace(0, VCC, NUM_MEDICIONES) 

for idx_medicion, v_val in enumerate(v_val_list):
    
    #input("Adquisicion %d - Presione una tecla para medir."%(idx_medicion+1))
    print('Midiendo %0.3f V'%v_val)

    MiGenArb.continua(v_val)
    
    # Mido tantas veces como indique
    for idx_sample in range(0,NUM_ADQUISICIONES):
        
        # Tomo una muestra
        matriz_medicion[idx_medicion,idx_sample] = get_count(port)
        # Espero antes de volver a pedir
        sleep(WAIT_MS/1000.0)
    print(matriz_medicion[idx_medicion,:].mean())
    escribir_en_csv(v_val,matriz_medicion[idx_medicion])
    
MiGenArb.close()
port.close()