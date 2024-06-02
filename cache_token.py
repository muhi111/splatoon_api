import pickle
from datetime import datetime

filename = 'tokens.pickle'

def cache_data(gtoken, bullet_token):
    timestamp = datetime.now()
    data = {'gtoken': gtoken, 'bullet_token': bullet_token, 'timestamp': timestamp}
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def load_data():
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None