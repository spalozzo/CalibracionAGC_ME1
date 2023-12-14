import threading
import time
from scipy.signal import resample
import numpy as np
from collections import deque

### VISA
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

# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)

class HandlerMediciones:
    def __init__(self, callback):

        self.fs_audio = 44100
        self.fs_osciloscopio = 100000 # hardcodear segun la fbt

        self.callback = callback
        self.thread = None

        self.buffer_size = int(self.fs_audio * 5)
        self.medicionesLeft  = deque(maxlen=self.buffer_size)
        self.medicionesRight = deque(maxlen=self.buffer_size)
        self.fAbort = False

        self.flagMuestreando = False  # Indica si el usuario le dio a startMuesreo

        # Inicializar pyvisa 1 y 2
        # Para q la pantlla del osc abarque 100ms aprox (lo mas cercano posible)
        
        ### Inicializacion PyVisa
        
        ### OSCILOSCOPIO 1
        
        USE_DEVICE_1 = 1

        # Abrimos el instrumento
        platforma1 = platform.platform()
        print(platforma1)
        rm=visa.ResourceManager()

        # El handle puede controlar osciloscopios, analizadores, etc.
        # Es generico
        instrument_handler1=rm.open_resource(rm.list_resources()[USE_DEVICE_1])

        # Creo el Osciloscopio
        self.MiOsciloscopio1 = GW_Instek(instrument_handler1)

        # Informamos el modelo del osciloscopio conectado
        print("Esta conectado un %s"%self.MiOsciloscopio1.INSTR_ID)
        
        USE_DEVICE_2 = 2
        
        ### OSCILOSCOPIO 2
        
        # Abrimos el instrumento
        platforma2 = platform.platform()
        print(platforma2)
        rm=visa.ResourceManager()

        # El handle puede controlar osciloscopios, analizadores, etc.
        # Es generico
        instrument_handler2=rm.open_resource(rm.list_resources()[USE_DEVICE_2])

        # Creo el Osciloscopio
        self.MiOsciloscopio2 = GW_Instek(instrument_handler2)

        # Informamos el modelo del osciloscopio conectado
        print("Esta conectado un %s"%self.MiOsciloscopio2.INSTR_ID)
        

    """
    Empieza a capturar pantallas del osciloscopio de 4seg
    Cada vez que termina de guardar un stream de datos se llama a la funcion "callback"
    que le pasaron al constructor de la API.
    Para medir lanza un thread (es una funcion no bloqueante)
    """

    def startMuestreo(self):
        if not self.flagMuestreando:
            self.flagMuestreando = True
            self.thread = threading.Thread(target=self.threadMediciones)
            self.thread.start()

    """
    Hace que ya no se llame más a la función de callback
    Elimina el thread si se estaba ejecutando
    """

    def stopMuestreo(self):
        self.flagMuestreando = False

    def isSampling(self):
        return self.flagMuestreando

    def readaptarFreqMuestreo(self, left, right, len_original):
        factor_resample = self.fs_audio / self.fs_osciloscopio
        num_puntos_resample = int(len_original * factor_resample)
        left44k1 = resample(left, num_puntos_resample)
        right44k1 = resample(right, num_puntos_resample)
        return left44k1, right44k1

    def medirIzq(self):
        tiempo1, tension1= self.MiOsciloscopio1.get_trace("1",VERBOSE=False)
        tiempo2, tension2= self.MiOsciloscopio1.get_trace("2",VERBOSE=False)
        
        tension_dif= tension1 - tension2
        #tension_dif= sig.savgol_filter(tension_dif, 4000,50)
        
        return tiempo1, tension_dif

    def medirDer(self):
        tiempo1, tension1= self.MiOsciloscopio2.get_trace("1",VERBOSE=False)
        tiempo2, tension2= self.MiOsciloscopio2.get_trace("2",VERBOSE=False)
        
        tension_dif= tension1 - tension2
        #tension_dif= sig.savgol_filter(tension_dif, 4000,50)
        
        return tiempo1, tension_dif

    def threadMediciones(self):
        while not self.fAbort:
            # Espero a que se complete la pantalla de 100mS
            # Ajustar al tiempo que vos puedas configurar
            time.sleep(0.1) #Tiempo en segundos, tiene que ser igual al tiempo que muestra el osc

            # Pido al Pyvisa que mida
            tl, muestrasLeft = self.medirIzq()
            tr, muestrasRight = self.medirDer()


            # Adapto valor de tensión a int16_t
            # Santi, chequear:
            # si va entre 0v-5v: dejar /5
            # si va entre -5v y 5v: poner /10
            muestrasLeft = muestrasLeft * (2 ** 16 - 1) / 5
            muestrasRight = muestrasRight * (2 ** 16 - 1) / 5

            # Readapto muestras a 44.1kHz
            left44k1, right44k1 = self.readaptarFreqMuestreo(muestrasLeft, muestrasRight, len(muestrasLeft))

            # Guardo muestras
            self.medicionesLeft.extend(left44k1)
            self.medicionesRight.extend(right44k1)

            # Verifico que haya un stream de 3 seg
            cantMuestras3seg = self.fs_audio*3
            if len(self.medicionesLeft) < cantMuestras3seg:
                continue

            # Agrupo en matriz
            num_elements = int(self.fs_audio * 3)
            slice3segLeft = np.array(self.medicionesLeft)[:num_elements]
            slice3segRight = np.array(self.medicionesRight)[:num_elements]
            muestras = np.vstack((slice3segLeft, slice3segRight))

            # Elimino 0.4seg
            num_elements = int(self.fs_audio * 0.4)
            for _ in range(num_elements):
                self.medicionesLeft.popleft()
                self.medicionesRight.popleft()

            # Llamo al callback de que termino de ejecutarse
            self.callback(muestras)


def generar_senoidal_prueba(frecuencia=1000, amplitud=5, duracion=0.1, frecuencia_muestreo=100000):
    tiempo = np.arange(0, duracion, 1 / frecuencia_muestreo)
    senoidal = amplitud * np.sin(2 * np.pi * frecuencia * tiempo)
    return tiempo, senoidal
