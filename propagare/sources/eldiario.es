"""
Propagare - 2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with Propagare; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
----------------

Regex magic keywords to extract data from: eldiario.es

"""
art_url==<a class="lnk" href="(.+?)
art_author==<a href="/autores/(.+?)/"
art_author2==red_n': '(.+?)' 
art_time=="dateCreated" : "(.+?)",
art_title==og:title" content="(.+?)/>
art_description==og:description" content="(.+?)/>
art_body==<p class="mce">(.+?)</p>
art_body2==<p class="mce"> (.+?)
