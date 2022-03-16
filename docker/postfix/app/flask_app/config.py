# Cette chaîne nous permet de nous connecter à la bdd
# bdd_uri = "postgresql://postgres:nael2001@127.0.0.1:5432/test"
from decouple import config

# bdd_uri = { 'pguser':'postgres',
# 'pgpasswd':'nael2001',
# 'pghost':'localhost',
# 'pgport': 5432,
# 'pgdb':'test'}


DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')
DB_NAME = config('DB_NAME')

bdd_uri = {
        'pguser': DB_USER,
        'pgpasswd':DB_PASSWORD,
        'pghost':DB_HOST,
        'pgport': DB_PORT,
        'pgdb':DB_NAME
        }

mdp_admin = "nael2001"

mdp_captcha = "nael2001"

mdp_adminnohash = "nael2001"


site_key = '6LfJt0IeAAAAAJzXffa3y4XckjEa3IHRYiQtQ54U'
secret_key = '6LfJt0IeAAAAAJgNyIow5R81ACZPnk6ZKTC5-FHQ'
# site_key = '6LfAIpIeAAAAAIwhkZcm3lpxLWGEwFVDyD--P0Jf'
# secret_key = '6LfAIpIeAAAAAI2mn-My9_dXjG9qZ1E3loImHKms'


ACCEPTED=1
REFUSED=2
UNDECIDED=3
