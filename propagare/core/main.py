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
import os, sys, urllib2, ssl, random, re, time, string
import json, operator, io
try:
    import html2text
except:
    print "\n[Error] - No se encuentra la librería: html2text. \n\n Puedes instalarla ejecutando en la terminal:\n\n   sudo apt-get install python-html2text\n\n Después, prueba a lanzar de nuevo la aplicación.\n"
    sys.exit(2)
from core.options import PropagareOptions
from core.update import Updater
reload(sys)
sys.setdefaultencoding('utf-8') # for decode byte (black magic!)

DEBUG = False

class Propagare(object):
    def __init__(self):
        self.supported_media = ["elpais.com", "eldiario.es", "elmundo.es"] # media sources modules currently implemented
        self.check_verb_online = "https://www.esfacil.eu/es/verbos/conjugacion.html?infinitive=" # for check spanish verbs online
        self.sources = [] # used for news media sources
        self.agents_file = 'core/txt/user-agents.txt' # set source path to retrieve user-agents
        self.referer = 'http://127.0.0.1/' # set referer
        self.agents = []
        f = open(self.agents_file)
        agents = f.readlines()
        f.close()
        for agent in agents:
            self.agents.append(agent) # agents are random each request
        self.ctx = ssl.create_default_context() # creating context to bypass SSL cert validation (black magic!)
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.jdata = [] # json stream container (a list)
        self.verbs = [] # a list to store semantics (verbs)
        self.total_verbs = 0
        self.total_num = 0

    def set_options(self, options):
        self.options = options

    def create_options(self, args=None):
        self.optionParser = PropagareOptions()
        self.options = self.optionParser.get_options(args)
        if not self.options:
            return False
        return self.options

    def remove_punctuation(self, news):
        p = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        no_p = ""
        for c in news:
            if c not in p:
                no_p = no_p + c
        news = no_p           
        return news

    def update_progress(self, t, p, l):
        b = p*100/l
        msg = "\r{0}: [{1}] {2}%".format(t, "#"*p + "-"*(l-p), round(b,2))
        if p >= 100: msg += " DONE\r\n"
        sys.stdout.write(msg)
        sys.stdout.flush()

    def banner(self):
        print '='*75
        print "  ____                                              _       "
        print " |  _ \ Si no 'contesta'...(es)__ _  __ _ _ __   __| | __ _ "
        print " | |_) | '__/ _ \| '_ \ / _` |/ _` |/ _` | '_ \ / _` |/ _` |"
        print " |  __/| | | (_) | |_) | (_| | (_| | (_| | | | | (_| | (_| |"
        print " |_|   |_|  \___/| .__/ \__,_|\__, |\__,_|_| |_|\__,_|\__,_|"
        print "                 |_|          |___/                (IA)v:0.1"
        print "\n"+'='*75
        print "\n"+self.optionParser.description
        print "\n"+'='*75

    @classmethod
    def try_running(cls, func, error, args=None):
        args = args or []
        try:
            return func(*args)
        except Exception:
            print(error, "error")
            if DEBUG == True:
                traceback.print_exc()

    def generate_json(self, n, category, date, tag, ID):
        if "elpais.com" in n:
            self.json_report = open('data/'+n+"/"+category+"/"+date+"/"+tag+"/"+ID+"/"+ID+".json", "w") 
        if "eldiario.es" in n:
            self.json_report = open('data/'+n+"/"+category+"/"+ID+"/"+ID+".json", "w")
        if "elmundo.es" in n:
            if tag is None:
                self.json_report = open('data/'+n+"/"+category+"/"+date+"/"+ID+".json", "w")
            else:
                self.json_report = open('data/'+n+"/"+category+"/"+date+"/"+tag+"/"+ID+".json", "w")

    def format_content(self, data):
        html_parser = html2text.HTML2Text()
        html_parser.ignore_links = True
        html_parser.ignore_images = True
        html_parser.ignore_emphasis = True
        html_parser.bypass_tables = True 
        html_parser.unicode_snob = True
        html_parser.skip_internal_links = True
        parsed = html_parser.handle(data)
        parsed = parsed.replace("\n", " ") # clean \n
        parsed = parsed.replace('\"', " ") # clean \"
        parsed = parsed.replace("#","") # clean #
        return parsed

    def count_all_stored(self): # all sources
        art_stored = 0
        for root, dirs, files in os.walk('data/'):
            art_stored += len(files) 
        return (art_stored-1)/2 # ((txt+json)-last_log)/2

    def count_art_stored(self, n): # by source
        art_stored = 0
        for root, dirs, files in os.walk('data/' + n):
            art_stored += len(files)
        return art_stored/2 # (txt+json)/2

    def count_sources_list(self):
        media_stored = 0
        for root, dirs, files in os.walk("data/"):
            for d in dirs:
                if d in self.supported_media:
                    media_stored = media_stored + 1
        return media_stored

    def check_art_exists(self, a, n):
        sep = ".json"
        for root, dirs, files in os.walk('data/' + n):
            for f in files:
                if f.endswith(".json"):
                    f = str(f.split(sep, 1)[0])
                    if str(f) in str(a):
                        check_pass = False
                        return check_pass
                    else:
                        check_pass = True

    def create_sources_list(self):
        for root, dirs, files in os.walk("sources/", topdown=False):
            for name in files:
                if name not in self.sources and name in self.supported_media:
                    self.sources.append(name) # add name to sources list     

    def check_art_repetitions(self, n, art_url_found):
        sep = "/"
        sep2 = ".html"
        sep3 = "."
        sep4 = "_"
        filenames = []
        for root, dirs, files in os.walk('data/' + n):
            for f in files:
                filename = os.path.basename(f)
                filename = str(filename.split(sep3, 1)[0])
                if not filename in filenames:
                    filenames.append(filename)
        if filenames:
            for f in filenames:
                for a in art_url_found:
                    if "eldiario.es" in n:
                        if str(f) in str(a):
                            art_url_found.remove(a)
                    if "elpais.com" in n:
                        f = str(f.split(sep3, 1)[0])
                        ID = str(a.split(sep, 5)[5]) 
                        ID = str(ID.split(sep2, 1)[0])
                        if sep in ID:
                            ID = str(ID.split(sep, 2)[2])
                        if str(ID) in str(f): # art stored, discard it
                            art_url_found.remove(a)
        return art_url_found

    def is_a_verb(self, w):
        if w.endswith("ar") or w.endswith("er") or w.endswith("ir"): # (spanish: inifitive verb)
             self.total_verbs = self.total_verbs + 1
             self.verbs.append(w) # add verb to list 

    def check_verb(self, verb):
        check_verb_online = str(self.check_verb_online) + verb # url + verb
        self.user_agent = random.choice(self.agents).strip() # suffle user-agent
        headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
        try:
            reply = urllib2.urlopen(check_verb_online, context=self.ctx).read()
        except: 
            print('\n[Error] - Imposible conectar con: ') + check_verb_online + '\n'
            return False
        if "¡Verbo no válido!" in reply or "¡Verbo no encontrado!" in reply: # working at: 30/04/2018
            return False
        else:
            return True

    def generate_data_stream(self):
        if self.options.ssource:
            if self.options.ssource in self.supported_media: # source is supported
                source = 'data/' + self.options.ssource
            else:
                print "-"*25
                print('\n[Error] La fuente indicada de estadísticas no está soportada! \n')
                print "-"*25
                print("\n[Info] Listado de fuentes soportadas :\n")
                n = 0
                for m in self.supported_media:
                    n = n + 1
                    print "    + ["+str(n)+"]:", m
                print "" # zen out
                sys.exit(2)
        else:
            source = 'data/'
        if self.options.tsource:
            if self.options.tsource in self.supported_media: # source is supported
                source = 'data/' + self.options.tsource
            else:
                print('\n[Error] La fuente indicada de búsqueda no está soportada! \n')
                print "-"*25
                print("\n[Info] Listado de fuentes soportadas :\n")
                n = 0
                for m in self.supported_media:
                    n = n + 1
                    print "    + ["+str(n)+"]:", m
                print "" # zen out
                sys.exit(2)
        else:
            if not self.options.ssource:
                source = 'data/'
        for root, dirs, files in os.walk(source): # generate stream for analisis             
            for fl in files:
                if fl.endswith(".json"): # extract content from json archives
                    p=os.path.join(root,fl)
                    kf = io.open(os.path.abspath(p), encoding='utf-8') 
                    try:
                        data = str(kf.read().encode('utf-8'))
                    except:
                        data = kf.read()
                    try:
                        self.jdata.append(json.loads(data))
                    except:
                        pass
                    kf.close()
        if not self.jdata:
            print "\n[Info] Necesitas extraer (-e) antes los datos, desde las fuentes.\n"
            print "[Info] Tienes el almacén vacío. Saliendo...\n"
            sys.exit(2) # return
        self.body_news_stream = []
        self.dates_news_stream = []
        self.author_news_stream = []
        self.entry_news_stream = []
        self.title_news_stream = []
        #self.url_news_stream = []
        for record in self.jdata:
            for key, value in record.iteritems(): # unpack a 'huge-stream' dict, stored on a list (a tuple) using iteritems() (black magic!)
                if key == "Noticia": # parse only for body content
                    self.body_news_stream.append(value)
                if key == "Fecha de publicación": # parse only for dates
                    self.dates_news_stream.append(value)
                if key == "Autor(a)": # parse only for authors
                    self.author_news_stream.append(value)
                if self.options.term: # extract more keys when searching a term
                    if key == "Entrada": # parse only for entry content
                        self.entry_news_stream.append(value)
                    if key == "Titular": # parse only for title
                        self.title_news_stream.append(value)
                    #if key == "Fuente": # parse only for url source
                    #    self.url_news_stream.append(value)

    def stats(self):
        print "\n[Info] Recopilando estadísticas del almacén...\n"
        all_art_stored = self.count_all_stored()
        if all_art_stored == 0 or all_art_stored < 0:
            print '-'*25
            print "\n[Info] Necesitas extraer (-e) antes los datos, desde las fuentes.\n" 
            print "[Info] Tienes el almacén vacío. Saliendo...\n" 
            return
        else:
            print "-"*25
            json_stats = open('data/last_stats.json', "w") # generate json with last stats
            json_stats_data = {}
            self.generate_data_stream() # generate a 'buffer' stream with records (using json files)
            self.create_sources_list()
            media_sources = self.count_sources_list()
            print "\n [+] Total medios:", str(media_sources)
            print " [+] Total noticias:", str(all_art_stored) + "\n"
            json_stats_data.update({"Total medios": str(media_sources)})
            json_stats_data.update({"Total noticias": str(all_art_stored)})        
            news_letters = 0
            symbols = []
            letters_dict = {}
            words_dict = {}
            words_3_dict = {}
            words_4_dict = {}
            words_5_dict = {}
            words_6_dict = {}
            words_7_dict = {}
            words_8_dict = {}
            verbs_dict = {}
            authors_dict = {}
            letters_counter = 0
            words_counter = 0
            verbs_counter = 0
            authors_counter = 0
            for news in self.body_news_stream:
                news_parsed = self.remove_punctuation(str(news)) # remove punctuation signs / encode from unicode to str
                news_parsed_noblank = news_parsed
                news_parsed_noblank.replace(" ","") # data as a stream without blank spaces
                news_parsed_noblank = news_parsed_noblank.lower() # change stream to lowercase
                news_letters = news_letters + len(news_parsed_noblank)
                news_split = news_parsed.split()
                nums = "0123456789" # 0-9
                symbols = map(chr, range(97, 123)) # a-z (A-Z)
                for char in nums:
                    symbols.append(char)
                for l in symbols:
                    if l in news_parsed_noblank: # only count those letters that exists
                        letters_counter = int(letters_counter + news_parsed_noblank.count(l))
                        if l in letters_dict.iteritems():
                            g = int(letters_dict[l]) # extract previous value
                        else:
                            g = 0
                        lg = letters_counter + g # sum new letters counted to previous ones
                        letters_dict.update({l:lg}) # update dict with new value
                        letters_counter = 0 # flush counter
                for w in news_split:
                    w = w.lower() # change word to lowercase
                    if w in words_dict:
			words_counter = words_counter + 1  
                        g = int(words_dict[w]) 
                    else:
                        g = 1 
                    words_counter = words_counter + g
                    words_dict.update({w:words_counter}) 
                    words_counter = 0
                    if self.options.checkverbs: 
                        self.is_a_verb(w) # check for verbs (adding to a list) using semantic rules        
            for key, value in words_dict.iteritems():
                if len(key) == 3:
                    words_3_dict[key] = value
                if len(key) == 4:
                    words_4_dict[key] = value
                if len(key) == 5:
                    words_5_dict[key] = value
                if len(key) == 6:
                    words_6_dict[key] = value
                if len(key) == 7:
                    words_7_dict[key] = value
                if len(key) > 7:
                    words_8_dict[key] = value
            if self.options.ssource:
                print '-'*25
                print "\n[Info] Mostrando estadísticas para:", str(self.options.ssource) + "\n"
            print " [+] Noticia más antigua:",str(min(self.dates_news_stream))
            print " [+] Noticia más reciente:",str(max(self.dates_news_stream)) + "\n"
            json_stats_data.update({"Noticia más antigua": str(min(self.dates_news_stream))})
            json_stats_data.update({"Noticia más reciente": str(max(self.dates_news_stream))})
            print " [+] Total símbolos (a-Z/0-9):", str(news_letters) + " (diferentes: "+ str(len(letters_dict)) + ")"  
            json_stats_data.update({"Total símbolos (a-Z/0-9)": str(news_letters) + " (diferentes: "+ str(len(letters_dict)) + ")"  }) 
            if max(letters_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                lw_max = "vez"
            else:
                lw_max = "veces"
            print " [+] Símbolo más utilizado: '"+str(max(letters_dict.iteritems(), key=operator.itemgetter(1))[0]).encode('utf-8').strip() + "' ("+ str(max(letters_dict.iteritems(), key=operator.itemgetter(1))[1])+ " " + lw_max + ")"
            json_stats_data.update({"Símbolo más utilizado": "'"+str(max(letters_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(max(letters_dict.iteritems(), key=operator.itemgetter(1))[1])+ " " + lw_max + ")"}) 
            if min(letters_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                lw_min = "vez"
            else:
                lw_min = "veces"
            print " [+] Símbolo menos repetido: '"+ str(min(letters_dict.iteritems(), key=operator.itemgetter(1))[0]).encode('utf-8').strip() + "' ("+ str(min(letters_dict.iteritems(), key=operator.itemgetter(1))[1])+ " " + lw_min + ")" + "\n"
            json_stats_data.update({"Símbolo menos repetido": "'"+str(min(letters_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(min(letters_dict.iteritems(), key=operator.itemgetter(1))[1])+ " " + lw_min + ")"}) 
            print " [+] Total palabras:", str(sum(words_dict.values())) + " (diferentes: "+ str(len(words_dict)) + ")"  
            json_stats_data.update({"Total palabras": str(sum(words_dict.values())) + " (diferentes: "+ str(len(words_dict)) + ")" }) 
            if max(words_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                lw_max = "vez"
            else:
                lw_max = "veces"
            print " [+] Palabra más repetida: '"+ str(max(words_dict.iteritems(), key=operator.itemgetter(1))[0]).encode('utf-8').strip() + "' ("+ str(max(words_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"
            json_stats_data.update({"Palabra más repetida":  "'"+str(max(words_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(max(words_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"}) 
            if max(words_3_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                lw_max = "vez"
            else:
                lw_max = "veces"
            print "      - 3 letras: '"+ str(max(words_3_dict.iteritems(), key=operator.itemgetter(1))[0]).encode('utf-8').strip() + "' ("+ str(max(words_3_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"
            json_stats_data.update({"Palabra más repetida (3 letras)":  "'"+str(max(words_3_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(max(words_3_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"}) 
            if max(words_4_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                lw_max = "vez"
            else:
                lw_max = "veces"
            print "      - 4 letras: '"+ str(max(words_4_dict.iteritems(), key=operator.itemgetter(1))[0]).encode('utf-8').strip() + "' ("+ str(max(words_4_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"
            json_stats_data.update({"Palabra más repetida (4 letras)":  "'"+str(max(words_4_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(max(words_4_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"}) 
            if max(words_5_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                lw_max = "vez"
            else:
                lw_max = "veces"
            print "      - 5 letras: '"+ str(max(words_5_dict.iteritems(), key=operator.itemgetter(1))[0]).encode('utf-8').strip() + "' ("+ str(max(words_5_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"
            json_stats_data.update({"Palabra más repetida (5 letras)":  "'"+str(max(words_5_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(max(words_5_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"}) 
            if max(words_6_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                lw_max = "vez"
            else:
                lw_max = "veces"
            print "      - 6 letras: '"+ str(max(words_6_dict.iteritems(), key=operator.itemgetter(1))[0]).encode('ISO-8859-1').strip() + "' ("+ str(max(words_6_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"
            json_stats_data.update({"Palabra más repetida (6 letras)":  "'"+str(max(words_6_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(max(words_6_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"}) 
            if max(words_7_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                lw_max = "vez"
            else:
                lw_max = "veces"
            print "      - 7 letras: '"+ str(max(words_7_dict.iteritems(), key=operator.itemgetter(1))[0]).encode('utf-8').strip() + "' ("+ str(max(words_7_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"
            json_stats_data.update({"Palabra más repetida (7 letras)":  "'"+str(max(words_7_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(max(words_7_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"}) 
            if max(words_8_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                lw_max = "vez"
            else:
                lw_max = "veces"
            print "      - 8+ letras: '"+ str(max(words_8_dict.iteritems(), key=operator.itemgetter(1))[0]).encode('utf-8').strip() + "' ("+ str(max(words_8_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")" + "\n"
            json_stats_data.update({"Palabra más repetida (8 letras)":  "'"+str(max(words_8_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(max(words_8_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"}) 
            if min(words_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                lw_min = "vez"
            else:
                lw_min = "veces"
            print " [+] Palabra menos repetida: '"+ str(min(words_dict.iteritems(), key=operator.itemgetter(1))[0]).encode('utf-8').strip() + "' ("+ str(min(words_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_min + ")"
            json_stats_data.update({"Palabra menos repetida":  "'"+str(min(words_dict.iteritems(), key=operator.itemgetter(1))[0]) + "' ("+ str(min(words_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_min + ")"}) 
            if max(words_8_dict.iteritems(), key=len)[1] < 2:
                lw_max = "vez"
            else:
                lw_max = "veces"
            print " [+] Palabra más larga y que más se usa: '"+ str(max(words_8_dict.iteritems(), key=len)[0]).encode('ISO-8859-1').strip() + "' ("+ str(max(words_8_dict.iteritems(), key=len)[1]) + " " + lw_max + ")" + "\n"
            json_stats_data.update({"Palabra más larga y que más se usa":  "'"+str(max(words_8_dict.iteritems(), key=len)[0]).encode('ISO-8859-1').strip() + "' ("+ str(max(words_8_dict.iteritems(), key=len)[1]).encode('ISO-8859-1').strip() + " " + lw_max + ")"}) 
            if self.options.checkverbs: 
                verb_flag = False
                num = 0
                print "[Info] Analizando (requiere tiempo!) en busca de: 'verbos infinitivos'...\n"
                for verb in self.verbs:
                    num = num + 1
                    verb_flag = self.check_verb(verb) # re-check previous list of verbs (online!)
                    if verb_flag is True: # is a verb
                        if verb in verbs_dict:
			    verbs_counter = verbs_counter + 1  
                            g = int(verbs_dict[verb]) 
                        else:
                            g = 1 
                        verbs_counter = verbs_counter + g
                        verbs_dict.update({verb:verbs_counter}) 
                        verbs_counter = 0
            if not verbs_dict:
                num_verbs = 0
                dif_verbs = 0
            else:
                num_verbs = str(sum(verbs_dict.values()))
                dif_verbs = str(len(verbs_dict))
            if verbs_dict:
                if self.options.checkverbs:
                    print " [+] Total verbos (infinitivos):", str(self.total_verbs) + " (diferentes: "+ str(dif_verbs) + ")"
                    json_stats_data.update({"Total verbos (infinitivos)": str(self.total_verbs) + " (diferentes: "+ str(dif_verbs) + ")"}) 
                    if max(verbs_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                        lw_max = "vez"
                    else:
                        lw_max = "veces"
                    print " [+] Verbo (infinitivo) más utilizado: '"+ str(max(verbs_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(max(verbs_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"
                    json_stats_data.update({"Verbo (infinitivo) más utilizado": str(max(verbs_dict.iteritems(), key=operator.itemgetter(1))[0])+ "' ("+ str(max(verbs_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_max + ")"}) 
                    if min(verbs_dict.iteritems(), key=operator.itemgetter(1))[1] < 2:
                        lw_min = "vez"
                    else:
                        lw_min = "veces"
                    print " [+] Verbo (infinitivo) menos repetido: '"+ str(min(verbs_dict.iteritems(), key=operator.itemgetter(1))[0]) + "' ("+ str(min(verbs_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_min + ")" + "\n"
                    json_stats_data.update({"Verbo (infinitivo) menos repetido": str(min(verbs_dict.iteritems(), key=operator.itemgetter(1))[0]) + "' ("+ str(min(verbs_dict.iteritems(), key=operator.itemgetter(1))[1]) + " " + lw_min + ")"}) 
            for a in self.author_news_stream:
                if a in authors_dict:
		    authors_counter = authors_counter + 1  
                    g = int(authors_dict[a]) 
                else:
                    g = 1 
                authors_counter = authors_counter + g
                authors_dict.update({a:authors_counter}) 
                authors_counter = 0
            print " [+] Total periodistas:", str(len(authors_dict.items()))
            json_stats_data.update({"Total periodistas": str(len(authors_dict.items()))}) 
            print " [+] Noticias por periodista:"
            sep = "/"
            num = 0
            for a, c in sorted(authors_dict.items(), key=lambda x: x[1], reverse=True):
                num = num + 1
                if c < 2:
                    lg = "noticia"
                else:
                    lg = "noticias"
                a = unicode(a)
                a = str(a.encode('utf-8').encode('ISO-8859-1'))
                print "      - '"+str(a).title() + "' ("+ str(c) + " " + lg + ")"
                json_stats_data["Autor(a)-["+str(num)+"]"] = str(a).title() + "' ("+ str(c) + " " + lg + ")"
            json_stats.write(json.dumps(json_stats_data, sort_keys=True, indent=2, separators=(',', ':'), ensure_ascii=False)) # write stats to json file
            json_stats.close() # close .json                   

    def search(self):
        print "\n[Info] Generando índice de búsqueda...\n"
        all_art_stored = self.count_all_stored()
        if all_art_stored == 0:
            print '-'*25
            print "\n[Info] Necesitas extraer (-e) antes los datos, desde las fuentes.\n" 
            print "[Info] Tienes el almacén vacío. Saliendo...\n" 
            return
        else:
            print "-"*25
        self.generate_data_stream() # generate a 'buffer' stream with all records (using json files)
        term_reply = str(raw_input("\n $ Introduce una palabra (ej: corrupción): "))
        term_reply = " " + term_reply + " " # parse term_reply to use it as a single word
        counter_term = 0
        counter_term_body = 0
        counter_term_entry = 0
        counter_term_title = 0
        titles_stream = []
        for n in self.body_news_stream:
            if term_reply in n:
                counter_term_body = counter_term_body + 1
        for e in self.entry_news_stream:
            if term_reply in e:
                counter_term_entry = counter_term_entry + 1
        for t in self.title_news_stream:
            if term_reply in t:
                counter_term_title = counter_term_title + 1
                titles_stream.append(t)       
        counter_term = counter_term_body + counter_term_entry + counter_term_title
        if counter_term < 2 and counter_term > 0:
            ct = "vez"
        elif counter_term == 0:
            ct = "veces"
        else:
            ct = "veces"
        if counter_term_body < 2 and counter_term_body > 0:
            cb = "artículo"
        elif counter_term_body == 0:
            cb = "artículos"
        else:
            cb = "artículos"
        if counter_term_entry < 2 and counter_term_entry > 0:
            ce = "entrada"
        elif counter_term_entry == 0:
            ce = "entradas"
        else:
            ce = "entradas"
        if counter_term_title < 2 and counter_term_title > 0:
            cl = "titular"
        elif counter_term_title == 0:
            cl = "titulares"
        else:
            cl = "titulares"
        if self.options.tsource:
            print "\n" + '-'*25
            print "\n[Info] Mostrando resultados en:", str(self.options.tsource)
        print "\n [+] Aparece en: ("+str(counter_term_body)+" "+str(cb)+"), ("+str(counter_term_title)+" "+str(cl)+") y ("+str(counter_term_entry)+" "+str(ce)+")"
        print " [+] Sale un total de: ("+str(counter_term)+" "+str(ct)+")" + "\n"

    def run(self, opts=None):
        options = self.create_options(opts)
        self.set_options(options)
        options = self.options
        if options.update: # update tool
            self.banner()
            try:
                print("\n [Info] Tratando de actualizar a la última versión estable:\n")
                Updater()
            except:
                print("\n [Error] Algo ha ido mal!. Para hacer funcionar ésta opción, deberías clonar Propagare lanzando:\n")
                print("  $ git clone https://github.com/epsylon/propagare\n")
        if options.view_media: # show supported sources
            self.banner()
            print("\n[Info] Listado de fuentes soportadas:\n")
            n = 0
            for m in self.supported_media:
                n = n + 1
                print "    + ["+str(n)+"]:", m
            print "" # zen out
        if options.stats: # show archive stats
            self.banner()
            self.stats()
        if options.term: # start a 'semantic' search for a term
            self.banner()
            self.search()
        if options.news: # extract news (general run)
            try: 
                self.banner()
                print "\n[Info] Buscando las fuentes de datos...\n"
                print "[Info] Examinando el contenido en línea...\n"
                sep='=='
                sep2='?'
                art_url=''
                art_url_list=[]
                art_title=''
                art_author=''
                art_location=''
                num=0
                flag=True
                if options.esource: # user has set a specific source
                    if options.esource in self.supported_media: # source is supported
                        self.supported_media = options.esource
                    else:
                        print "-"*25
                        print('\n[Error] La fuente que has indicado no está soportada! \n')
                        print "-"*25
                        print("\n[Info] Listado de fuentes soportadas :\n")
                        n = 0
                        for m in self.supported_media:
                            n = n + 1
                            print "    + ["+str(n)+"]:", m
                        print "" # zen out
                        return
                self.create_sources_list()
                for n in self.sources: # n = news media source
                    if n.endswith(""):
                        n_url = n.replace("", "/")
                    if not n.startswith("http"):
                        if n == "elmundo.es": # this media only supports access using www
                            n_url = "https://www." + n
                        else:
                            n_url = "https://" + n # SSL only
                    print "- Visitando:", n_url
                    self.user_agent = random.choice(self.agents).strip() # suffle user-agent
                    headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set fake user-agent and referer
                    try:
                        reply = urllib2.urlopen(n_url, context=self.ctx).read()
                    except: 
                        print('\n[Error] - Imposible conectar con: ') + n
                        pass
                    f = open('sources/'+ n)
                    regex = f.readlines()
                    f.close()
                    #print reply # nice to have this output for dev new modules
                    for r in regex: # extract specific keywords from news: time, author, url (+variations), title, description, body
                        if ('art_url==' or 'art_url2==') in r:
                            art_url = r
                            regex_art_url = str(art_url.split(sep, 1)[1]) # regex magics (art_url)
                            pattern_art_url = re.compile(regex_art_url)
                        if 'art_author==' in r:
                            art_author = r
                            regex_art_author = str(art_author.split(sep, 1)[1]) # regex magics (art_author)
                            pattern_art_author = re.compile(regex_art_author)
                        if 'art_time==' in r:
                            art_time = r
                            regex_art_time = str(art_time.split(sep, 1)[1]) # regex magics (art_time)
                            pattern_art_time = re.compile(regex_art_time)
                        if 'art_title==' in r:
                            art_title = r
                            regex_art_title = str(art_title.split(sep, 1)[1]) # regex magics (art_title)
                            pattern_art_title = re.compile(regex_art_title)
                        if 'art_description==' in r:
                            art_description = r
                            regex_art_description = str(art_description.split(sep, 1)[1]) # regex magics (art_description)
                            pattern_art_description = re.compile(regex_art_description)
                        if 'art_body==' in r:
                            art_body = r
                            regex_art_body = str(art_body.split(sep, 1)[1]) # regex magics (art_body)
                            pattern_art_body = re.compile(regex_art_body, re.MULTILINE)
                    try:
                        art_url_found = re.findall(pattern_art_url, reply) # found art_url patterns on main page
                        art_url_parsed = self.check_art_repetitions(n, art_url_found) # discard results previously stored
                    except: 
                        art_url_parsed = None
                        pass
                    art_stored = self.count_art_stored(n)
                    if not art_url_parsed and not art_stored:
                        print "\n[Info] Nuevos artículos encontrados: 0 | Total artículos almacenados (de ésta fuente): 0\n"
                        return
                    if not art_url_parsed and art_stored > 0: # not any new article found + some articles stored 
                        pass
                    elif len(art_url_parsed) is 0 and art_stored is 0: # not any new article found + not any article stored
                        print "\n[Info] Nuevos artículos encontrados: 0 | Total artículos almacenados (de ésta fuente): " + str(art_stored) + "\n"
                        return
                    else: # new article found
                        print "" # zen out
                        for a in art_url_parsed:
                            if "elmundo.es" in n: # re-parsing website: elmundo.es [10/05/2018]
                                if '"' in a:
                                    a = str(a.split('"', 1)[0])
                                if '#' in a:
                                    a = str(a.split('#', 1)[0])
                                if not "http" in a or not "www.elmundo.es" in a or "vivienda" in a or "horoscopo" in a or "menu" in a or "?" in a or "indices" in a or "programacion-tv" in a:
                                    a = None
                            if "eldiario.es" in n: # re-parsing website: eldiario.es [09/05/2018]
                                if '" title="' in a:
                                    a = str(a.split('"', 1)[0])
                                if '">' in a:
                                    a = str(a.split('"', 1)[0])
                                if "rastreador" in a or "http" in a or "autores" in a or "www.eldiario.es" in a or "/carnecruda" in a or "/contenido_patrocinado" in a:
                                    a = None
                            if "elpais.com" in n: # re-parsing website: elpais.com [24/04/2018]
                                if "?" in a:
                                    a = str(a.split(sep2, 1)[0])
                                if "posicionador" in a:
                                    a = a.replace('" class="posicionador',"")
                                if "elpais.com" in a:
                                    a = "https:/" + a
                                else:
                                    a = n_url + "/" + a
                            if a is not None:
                                if "eldiario.es" in n: # re-parsing website: eldiario.es [09/05/2018]
                                    a = "https://eldiario.es" + a
                                if a not in art_url_list:
                                    check_pass = self.check_art_exists(a, n) # check if art found is previously stored for this media
                                    if check_pass is True or check_pass is None:
                                        art_url_list.append(a) # crawlered pages from main website
                                        print "    + [IA]:", a
                        if not art_url_list:
                            pass
                        else:
                            print "\n[Info] Nuevos artículos encontrados: " + str(len(art_url_list)) + " | Total artículos almacenados (de ésta fuente): " + str(art_stored) + "\n"
                            print "- Extrayendo:", n_url
                            if not os.path.exists('data/'):
                                os.makedirs('data/')
                            if not os.path.exists('data/' + n):
                                os.makedirs('data/' + n)
                            for a in art_url_list:
                                num=num+1 # art counter
                                json_data = {} # json dict stream buffer
                                if '"' in a: # re-parse url searching for " after it
                                    sep = '"'
                                    a = str(a.split(sep, 1)[0])
                                print "\n    + ["+str(num)+"/"+str(len(art_url_list))+"] Visitando:", a
                                self.user_agent = random.choice(self.agents).strip() # suffle user-agent
                                headers = {'User-Agent' : self.user_agent, 'Referer' : self.referer} # set user-agent and referer
                                try:
                                    reply_art = urllib2.urlopen(a, context=self.ctx).read()
                                except: 
                                    print('\n[Error] - Imposible conectar con: ') + a
                                    return
                                art_url_author_found = re.findall(pattern_art_author, reply_art) # found art_author pattern on page
                                if not art_url_author_found:
                                    for r in regex: # extract another combination
                                        if 'art_author2==' in r:
                                            art_author = r
                                            try:
                                                regex_art_author = str(art_author.split(sep, 1)[1]) # re-regex magics (art_author)
                                                pattern_art_author = re.compile(regex_art_author)
                                            except:
                                                break
                                    art_url_author_found = re.findall(pattern_art_author, reply_art) # try another art_author pattern on page
                                if not art_url_author_found: # not any author found using regex (use default for each media)
                                    if "elmundo.es" in n: # default author for elmundo.es when not signed
                                        art_url_author_found.append("Ediciones El Mundo")
                                    if "elpais.com" in n: # default author for elpais.com when not signed
                                        art_url_author_found.append("Ediciones El País")
                                    if "eldiario.es" in n: # default author for elpais.com when not signed
                                        art_url_author_found.append("Ediciones El Diario")
                                else:
                                    if "elpais.com" in n: # based on specific reg exp.
                                        sep = '"'
                                        for author in art_url_author_found:
                                            art_url_author_found.remove(author)
                                            author = str(author.split(sep, 1)[0])
                                            art_url_author_found.append(author)
                                art_url_time_found = re.findall(pattern_art_time, reply_art) # found art_time pattern on page
                                art_url_title_found = re.findall(pattern_art_title, reply_art) # found art_title pattern on page
                                art_url_description_found = re.findall(pattern_art_description, reply_art) # found art_description pattern on page 
                                art_url_body_found = re.findall(pattern_art_body, reply_art) # found art_body pattern on page (MULTILIN)
                                if not art_url_body_found: # not any body found
                                    if "eldiario.es" in n:
                                        for r in regex: # extract another combination
                                            if 'art_body2==' in r:
                                                art_body = r
                                                regex_art_body = str(art_body.split(sep, 1)[1])
                                                pattern_art_body = re.compile(regex_art_body)
                                        art_url_body_found = re.findall(pattern_art_body, reply_art) 
                                time.sleep(0.1) # tic, tac!!!
                                self.update_progress("\n      - ETA", num, len(art_url_list))
                                print "" # zen out
                                if "elmundo.es" in a: # [10/05/2018] # schema: https://www.elmundo.es/category/{tag}/date/ID
                                    a_path = a.replace("http://www.elmundo.es/","") # remove pre-url (note: http)
                                    a_path = a_path.replace(".html","") # remove post-url
                                if "elpais.com" in a: # [24/04/2018] # schema: https://elpais.com/category/date/tag/ID
                                    a_path = a.replace("https://elpais.com/","") # remove pre-url
                                    a_path = a_path.split(".html") # remove post-url
                                    if "elpais.com" in a_path: # re-parsing url [24/04/2018] # schema: https://loc.elpais.com/...
                                        a_path = a_path.split("elpais.com/")
                                        a_path = a_path[1]
                                if "eldiario.es" in a: # [08/05/2018] # schema: https://eldiario.es/category/{tag}/ID
                                    a_path = a.replace("https://eldiario.es/","") # remove pre-url
                                    a_path = a_path.replace(".html","") # remove post-url
                                if "/" in a_path: # / mostly used like url-category sep keyword
                                    a_path = a_path.split("/")
                                    if "elmundo.es" in a:
                                        try: # try with /tag/
                                            category = a_path[0]
                                            date_year = a_path[2]
                                            date_month = a_path[3]
                                            date_day = a_path[4]
                                            date = date_year + "_" + date_month + "_" + date_day # date: year/month/day
                                            tag = a_path[1]
                                            ID = a_path[5]
                                            if not os.path.exists('data/'+n+"/"+category):
                                                os.makedirs('data/'+n+"/"+category)
                                            if not os.path.exists('data/'+n+"/"+category+"/"+date):
                                                os.makedirs('data/'+n+"/"+category+"/"+date)
                                            if not os.path.exists('data/'+n+"/"+category+"/"+date+"/"+tag): # create new record
                                                os.makedirs('data/'+n+"/"+category+"/"+date+"/"+tag)
                                            path = 'data/'+n+"/"+category+"/"+date+"/"+tag+"/"+ID+".txt" # set path to file 
                                            self.generate_json(n, category, date, tag, ID) # generate .json  
                                        except:
                                            try:
                                                category = a_path[0]
                                                date_year = a_path[1]
                                                date_month = a_path[2]
                                                date_day = a_path[3]
                                                date = date_year + "_" + date_month + "_" + date_day # date: year/month/day
                                                ID = a_path[4]
                                                if not os.path.exists('data/'+n+"/"+category):
                                                    os.makedirs('data/'+n+"/"+category)
                                                if not os.path.exists('data/'+n+"/"+category+"/"+date):
                                                    os.makedirs('data/'+n+"/"+category+"/"+date)
                                                path = 'data/'+n+"/"+category+"/"+date+"/"+ID+".txt" # set path to file 
                                                self.generate_json(n, category, date, None, ID) # generate .json
                                            except:
                                                pass
                                    if "eldiario.es" in a:
                                        category = a_path[0]
                                        ID = a_path[1]
                                        if not os.path.exists('data/'+n+"/"+category):
                                            os.makedirs('data/'+n+"/"+category)
                                        if not os.path.exists('data/'+n+"/"+category+"/"+ID):
                                            os.makedirs('data/'+n+"/"+category+"/"+ID)
                                        path = 'data/'+n+"/"+category+"/"+ID+"/"+ID+".txt" # set path to file 
                                        self.generate_json(n, category, None, None, ID) # generate .json         
                                    if "elpais.com" in a:
                                        category = a_path[0]
                                        date_year = a_path[1] 
                                        date_month = a_path[2]
                                        date_day = a_path[3] 
                                        date = date_year + "_" + date_month + "_" + date_day # date: year/month/day
                                        tag = a_path[4]
                                        ID = a_path[5]
                                        if not os.path.exists('data/'+n+"/"+category):
                                            os.makedirs('data/'+n+"/"+category)
                                        if not os.path.exists('data/'+n+"/"+category+"/"+date):
                                            os.makedirs('data/'+n+"/"+category+"/"+date)
                                        if not os.path.exists('data/'+n+"/"+category+"/"+date+"/"+tag):
                                            os.makedirs('data/'+n+"/"+category+"/"+date+"/"+tag)
                                        if not os.path.exists('data/'+n+"/"+category+"/"+date+"/"+tag+"/"+ID): # create new record
                                            os.makedirs('data/'+n+"/"+category+"/"+date+"/"+tag+"/"+ID)  
                                        path = 'data/'+n+"/"+category+"/"+date+"/"+tag+"/"+ID+"/"+ID+".txt" # set path to file 
                                        self.generate_json(n, category, date, tag, ID) # generate .json
                                    try:
                                        fs = open(path, "w") # generate .txt
                                    except:
                                        print "\n[Error] No se pueden extraer las noticias de manera correcta. Saliendo...\n"
                                        return
                                    fs.write("Fuente: " + str(a).encode('utf-8') + "\n") # write source url
                                    json_data.update({"Fuente": str(a)})
                                    for t in art_url_time_found:
                                        fs.write("Fecha de publicación: " + str(t).encode('utf-8') + "\n") # write time
                                        json_data.update({"Fecha de publicación": str(t)})
                                    for author in art_url_author_found:
                                        if "\t" in author:
                                            author = author.split('\t', 1)[1] # re-parse for \t
                                        author = str(author.decode('ISO-8859-1').strip())
                                        fs.write("Autor(a): " + str(author).encode('utf-8') + "\n") # write author
                                        json_data.update({"Autor(a)": str(author)})
                                    for title in art_url_title_found:
                                        title = str(title.decode('ISO-8859-1').strip())
                                        parsed = self.format_content(str(title)) 
                                        fs.write("Titular: " + str(parsed).encode('utf-8') + "\n") # write title
                                        json_data.update({"Titular": str(parsed)})
                                    for description in art_url_description_found:
                                        description = str(description.decode('ISO-8859-1').strip())
                                        parsed = self.format_content(str(description))
                                        fs.write("Entrada: " + str(parsed).encode('utf-8') + "\n") # write description
                                        json_data.update({"Entrada": str(parsed)})
                                    body_complete = ""
                                    for body in art_url_body_found:
                                        body = str(body.decode('ISO-8859-1').strip())
                                        if "elmundo.es" in a:
                                            body = body.split("TE PUEDE INTERESAR",1)[0]
                                            if "###" in body:
                                                body = body.relace("###","")
                                        if "elpais.com" in a: 
                                            body = body.replace("<span>Explora nuestras historias</span> por temas","")
                                            body = body.replace("Recibe nuestra newsletter", "")
                                        body_complete += body + "\n\n"
                                        if "elmundo.es" in a:
                                            break
                                    parsed = self.format_content(body_complete) 
                                    fs.write("\n" + str(parsed).encode('utf-8')) # write (plain text) body without keyword
                                    json_data.update({"Noticia": str(parsed)})
                                    self.json_report.write(json.dumps(json_data, sort_keys=True, indent=2, separators=(',', ':'), ensure_ascii=False)) # json dump
                                    fs.close() # close .txt
                                    self.json_report.close() # close .json
                                    self.total_num = self.total_num + 1
                    num = 0 # flush art found counter
                    art_url_list = [] # flush art list
                all_art_stored = self.count_all_stored()
                if self.total_num:
                    print "" # zen out
                else:
                    self.total_num = 0
                print "\n[Info] Nuevos artículos descargados: " + str(self.total_num) + " | Total artículos almacenados (de todas las fuentes): " + str(all_art_stored) + "\n"
                if all_art_stored > 0:  
                    if not self.options.forceno:
                        print "-"*25
                        stats_reply = raw_input("¿Quieres ver las estadísticas comparadas (S/n)?\n")
                    else:
                        stats_reply = "N"
                    if stats_reply == "s" or stats_reply == "S":
                        self.stats()
                    else:
                        print "\n[Info] Saliendo...\n"
                        return
                    if not self.options.forceno:
                        print "-"*25
                        search_reply = raw_input("¿Quieres buscar información semántica (S/n)?\n")
                    else:
                        search_reply = "N"
                    if search_reply == "s" or search_reply == "S":
                        self.search()
                    else:
                        print "\n[Info] Saliendo...\n"
            except (KeyboardInterrupt, SystemExit):
                sys.exit()

if __name__ == "__main__":
    app = Propagare()
    app.run()
