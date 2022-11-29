import os

PROJECT_ROOT = os.path.dirname(__file__)
DATA_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, '..', "data/"))
SCRAPE_KEYS_FILEPATH = os.path.abspath(os.path.join(PROJECT_ROOT, '..', "data/tracking/scrape_keys.sqlite"))
