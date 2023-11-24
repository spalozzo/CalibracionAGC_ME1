# -*- coding: utf-8 -*-
"""
@author: Pablo, Ramiro

La idea es que esta clase tome un intrumento como entrada, junto con los datos
que necesita (como el canal de medición) y devuelva el valor solicitado 
utilizando la clase "mediciones".

Esta clase es un nivel de abstracción mas del osciloscopio donde podemos 
construir métodos de medición que utilicen varias mediciones en distintos
modos.

"""

import numpy as np
import mediciones
import matplotlib.pyplot as plt


class Operador_osciloscopio(mediciones.Mediciones):
    
    def __init__(self,inst,operador):
        # nombre del equipo dado por el usuario
        self.operador    = operador
        # Clase de instrumento
        self.instrument    = inst


    def medir_Vrms(self, canal = 1, VERBOSE = False):

        if VERBOSE:
            print("metodo de medicion realizado por {}".format(self.operador))
            print("con el instrumento {}".format(self.instrument.print_ID()))

        tiempo,tension = self.instrument.get_trace(canal, VERBOSE)

        return self.Vrms(tiempo,tension)
    
    def medir_detaF(self, canal = 1, VERBOSE = False):
        pass

    def medir_indiceMod(self, canal = 1, VERBOSE = False):
        pass

    def get_espectro(self, canal = 1, ventan='uniforme', VERBOSE = False):
        # devolver eje en frecuencia
        pass

    def medir_thd(self,canal=1,VERBOSE= False):
        if VERBOSE:
            print("metodo de medicion realizado por {}".format(self.operador))
            print("con el instrumento {}".format(self.instrument.print_ID()))

        tiempo,tension = self.instrument.get_trace(canal, VERBOSE)

        return self.THD(tiempo,tension)
        
    
    def medir_RC(self, R, ch_R = 1, ch_G = 2, metodo = "FFT"):
        
        '''
        Parameters
        ----------
        R : INT
            Valor de resistencia utilizado para medir el capacitor
        ch_R : TYPE
            canal utilizado para medir la tension en la R. (por defecto canal 1)
        ch_G : TYPE
            canal utilizado para medir la tension en el generador.(por defecto canal 2)
        metodo : {TIEMPO; LISSAJ; POT; FFT} string en mayusculas
           Metodo para calcular el capacitor. The default is "TIEMPO".
        
        Returns
        -------
        Valor del capacitor
        
        '''
        tiempo_gen,tension_gen = self.instrument.get_trace(ch_G, VERBOSE = False)
        tiempo_r,tension_r = self.instrument.get_trace(ch_R, VERBOSE = False)
        
        # Ploteamos los canales
        fig_RC= plt.figure(1)
        ax_RC, ax_R= fig_RC.subplots(2)

        fig_RC.sca(ax_RC)
        ax_RC.plot(tiempo_gen,tension_gen, label='Tension sobre RC')
        plt.legend()
        fig_RC.sca(ax_R)
        ax_R.plot(tiempo_r,tension_r, color='red', label='Tension sobre R')
        plt.legend()
        plt.show()
        
        tiempo_gen= [i*2 for i in tiempo_gen]
        cruce_cero= 0
        for i,j in zip(tension_r, tiempo_r):
            if i<=0.1 and i>=-0.1 and cruce_cero==0:
                cruce_cero= j
        
        frec= 1/cruce_cero/2
        print("FRECUENCIA=",frec)
        #return self.calculo_Capacitor(valor_r= R,frec=frec,tiempo= tiempo_gen,tension_r= tension_r,tension_gen= tension_gen)
        return self.calculo_Capacitor(R,frec,tiempo_gen,tension_r, tension_gen, metodo)

class Operador_generador(mediciones.Mediciones):
    
    def __init__(self,inst,operador):
        # nombre del equipo dado por el usuario
        self.operador    = operador
        # Clase de instrumento
        self.instrument    = inst

    def generar_FM(self, fc, fm, deltaF, cant_muestras, offset, sample_rate=100000):
        pass

    def generar_AM(self, fc, fm, M, cant_muestras, offset, sample_rate=100000):
        pass
