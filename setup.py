# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 13:53:05 2020

@author: Asja
"""
import os
from setuptools import setup

def readfile(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(name='bibliorecordsminer',
      version='1.0',
      description='''Extraction of text from pdf with publications list. 
      Splitting txt into bibliographic records. 
      Extraction publication years and types of publication''',
      author='Asia Mironenko',
      author_email='mironenkoasja@gmial.com',
      url='https://www.python.org/sigs/distutils-sig/',
      install_requires=['pandas', 'pdfminer']
     )