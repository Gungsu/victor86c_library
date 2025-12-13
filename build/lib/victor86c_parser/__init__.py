"""
Biblioteca Python para decodificar o protocolo de comunicação serial
do multímetro VICTOR 86C/86D.

Expõe a classe principal Victor86cParser para decodificação de pacotes brutos.
"""
from .parser import Victor86cParser

__all__ = ['Victor86cParser']