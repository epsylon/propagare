"""
Propagare - 2018 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with Propagare; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
----------------

Regex magic keywords to extract data from: elmundo.es

"""
art_url==<a href="(.+?)
art_author==<span itemprop="name">(.+?)</span>
art_author2==s.prop75="(.+?)";
art_time=="DC.date.issued" content="(.+?)">
art_title==og:title" content="(.+?)"/>
art_description==og:description" content="(.+?)"/>
art_body==<p>(.+?)
