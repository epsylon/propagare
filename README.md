  ![Propagare](https://03c8.net/images/propagare2.png "Propagare")

----------

 + Web:  https://propaganda.is

 + Código:  https://github.com/epsylon/propagare

----------

  Propagare  - es una herramienta de extracción, organización y análisis semántico de noticias.

----------

#### Instalando:

  Propagare es multiplataforma. Requiere Python (>2.7.9) y las siguientes librerías:

       python-html2text - Python module for converting HTML to Markdown text

  En sistemas basados en Debian (ej: Ubuntu), puedes instalarla mediante: 

       sudo apt-get install python-html2text

  O también puedes usar un script de instalación automática (adjunto con la herramienta), ejecutando:

       python setup.py install

  Incluso utilizando 'pip':

       pip install html2text

####  Fuentes de las librerías:

   * Python: https://www.python.org/downloads/
   * Pypi-html2text: https://pypi.org/project/html2text/

----------

####  Licencia:

  Propagare es distribuída con la licencia GPLv3. Puede revisarla en: [LICENSE](./docs/LICENSE).

----------

####  Opciones

       --version      muestra la versión del programa
       -h, --help     muestra la ayuda

       --update       actualiza la herramienta a su última versión

       --list         lista las fuentes de noticias soportadas

       -e             extrae noticias de todas las fuentes
       --es=ESOURCE   especifíca una fuente de donde extraer noticias
       --force-no     utilízalo para almacenar datos (Big Data)

       -s             muestra algunas estadísticas interesantes
       --ss=SSOURCE   especifíca una fuente de donde extraer estadísticas
       --check-verbs  chequea si una palabra es un verbo (Experimental)

       -t             busca el término en el almacén
       --ts=TSOURCE   busca el término en una fuente determinada

----------

  ![Propagare](https://03c8.net/images/propagare.png "Propagare")

  ![Propagare](https://03c8.net/images/propagare3.png "Propagare")
