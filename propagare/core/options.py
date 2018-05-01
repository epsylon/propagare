#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
Propagare - 2018 - by psy (epsylon@riseup.net)

-------
You should have received a copy of the GNU General Public License along
with Propagare; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
-------

"A diferencia del odio, el amor se expande sin necesidad de propaganda..."

"""
import optparse

class PropagareOptions(optparse.OptionParser):
    def __init__(self, *args):
        optparse.OptionParser.__init__(self, 
                           description=' Propagar(es): extracción, organización y análisis semántico de noticias.',
                           prog='propagare.py',
			   version='\nPropagare v0.1 - 2018 - GPLv3.0 -> por psy\n',
                           usage= 'propagare [OPTIONS]')
        self.add_option("--update", action="store_true", dest="update", help="actualiza la herramienta a su última versión")
        self.add_option("--list", action="store_true", dest="view_media", help="lista las fuentes de noticias soportadas")
        self.add_option("-e", action="store_true", dest="news", help="extrae noticias de todas las fuentes")
        self.add_option("--es", action="store", dest="esource", help="especifíca una fuente de donde extraer noticias")
        self.add_option("--force-no", action="store_true", dest="forceno", help="utilízalo para almacenar datos (Big Data)")
        self.add_option("-s", action="store_true", dest="stats", help="muestra algunas estadísticas interesantes")
        self.add_option("--ss", action="store", dest="ssource", help="especifíca una fuente de donde extraer estadísticas")
        self.add_option("--check-verbs", action="store_true", dest="checkverbs", help="chequea si una palabra es un verbo (Experimental)")
        self.add_option("-t", action="store_true", dest="term", help="busca el término en el almacén")
        self.add_option("--ts", action="store", dest="tsource", help="busca el término en una fuente determinada")
        #self.add_option("--timer", action="store", dest="timer", help="establece un tiempo para buscar nuevas noticias (en min.)")

    def get_options(self, user_args=None):
        (options, args) = self.parse_args(user_args)
        options.args = args
        if (not options.news and not options.stats and not options.term and not options.update and not options.view_media):
            print '='*75
            print "  ____                                              _       "
            print " |  _ \ Si no 'contesta'...(es)__ _  __ _ _ __   __| | __ _ "
            print " | |_) | '__/ _ \| '_ \ / _` |/ _` |/ _` | '_ \ / _` |/ _` |"
            print " |  __/| | | (_) | |_) | (_| | (_| | (_| | | | | (_| | (_| |"
            print " |_|   |_|  \___/| .__/ \__,_|\__, |\__,_|_| |_|\__,_|\__,_|"
            print "                 |_|          |___/                (IA)v:0.1"
            print "\n"+'='*75
            print "\n"+self.description
            print "\n"+'='*75
            print "\n [+] Opciones: -h o --help"
            print "\n"+'='*75 + "\n"
        return options
