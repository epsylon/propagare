#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
Propagare - 2018 - by psy (epsylon@riseup.net)

-------
You should have received a copy of the GNU General Public License along
with Propagare; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
-------

"A diferencia del odio, el amor se expande sin necesidad de propaganda."

"""
import os
from subprocess import PIPE
from subprocess import Popen as execute
        
class Updater(object):   
    def __init__(self):
        GIT_REPOSITORY = "https://github.com/epsylon/propagare"
        rootDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', ''))
        if not os.path.exists(os.path.join(rootDir, ".git")):
            print " [Info] No se ha encontrado ningún respositorio: .git!\n"
            print "="*30
            print "\n Para hacer funcionar ésta opción, debes clonar Propagare mediante:\n"
            print " $ git clone %s" % GIT_REPOSITORY + "\n"
        else:
            checkout = execute("git checkout . && git pull", shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
            print checkout
            if not "Already up-to-date" in checkout:
                print "Enhorabuena!! Propagare se ha actualizado... ;-)\n"
            else:
                print "Propagare no necesita actualización... ;-)\n"
