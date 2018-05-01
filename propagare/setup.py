#!/usr/bin/env python
import sys
if sys.version_info[0] != 2:
    sys.exit("Disculpa, Propagare necesita Python >= 2.7.9") 
from setuptools import setup, find_packages
setup(
    name='propagare',
    version='0.1',
    license='GPLv3',
    author_email='epsylon@riseup.net',
    author='psy',
    description='Extracción, organización y análisis semántico de noticias.',
    url='https://github.com/epsylon/propagare',
    long_description=open('docs/LEEME.txt').read(),
    packages=find_packages(),
    install_requires=['html2text'],
    include_package_data=True,
    package_data={
        'core': ['txt/*.txt'],
    },
    entry_points={
        'console_scripts': [
            'propagare=Propagare:core.main',
        ],
        'gui_scripts': [
            'propagare=Propagare:core.main',
        ],
    },
    keywords='Propaganda Analisis Estadísticas Noticias Periodistas BigData',
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Environment :: Console", 
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
        "Topic :: Internet", 
      ],
      zip_safe=False
)
