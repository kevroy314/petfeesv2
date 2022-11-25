from sqlitedict import SqliteDict
import os

files = os.listdir('./data')
sizes = [os.path.getsize(os.path.join('./data', x)) for x in files if x.endswith('-items.json.gz')]
db = SqliteDict('./data/tracking/scrape_keys.sqlite')
n = len(list(db.keys()))
mbs = sum(sizes)/1000000
nzips = 30001
zip_queries = [x for x in db.keys() if str(x).startswith('https://www.rent.com/zip-') and 'page' not in x]
total_zips = 30001
percent_complete_zips = len(zip_queries)/total_zips
print('n={}, size={:.2f}MB, average={:.3f}, {}/{} ({}%) zips complete, estimated_size_on_disk={:.2f}GB'.format(n, mbs, mbs/n, len(zip_queries), total_zips, percent_complete_zips, mbs/percent_complete_zips/1000))