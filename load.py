import os
import json

FILENAME_ROOT = './'
FILENAME_DATA = 'data/'
FILENAME_RES_DATA = 'res_sample.json'
FILENAME_RES_PHOTOS_DATA = 'photo_sample.json'
FILENAME_INSERT_QUERIES = 'insert.sql'

def get_data_file_path(filename):
  return os.path.join(FILENAME_ROOT, FILENAME_DATA, filename)

def convert_to_string(param):
  return '\'{}\''.format(param.replace("'", "''")) if param else 'NULL'

PATH_RES_DATA = get_data_file_path(FILENAME_RES_DATA)
PATH_INSERT_QUERY_FILE = get_data_file_path(FILENAME_INSERT_QUERIES)

'''
  id        INTEGER       PRIMARY KEY,
  name      VARCHAR(128)  NOT NULL,
  address   VARCHAR(128)  NOT NULL,
  phone     VARCHAR(32),
  website   VARCHAR(128),
  latitude  DECIMAL       NOT NULL,
  longitude DECIMAL       NOT NULL,
  status    INTEGER       NOT NULL,
  location  INTEGER       NOT NULL,
  owner_id  INTEGER,
'''

# INSERT INTO restaurants (id, name, address, phone, website, latitude, longitude, status, location, owner_id)
# VALUES (123,'Res Name','1234 adddress line','342352365324', 'https://google.com', 78, 65, 0, 1, 0);

file_dump = '''INSERT INTO status (sid, name)
VALUES (0, 'Closed'),
(1, 'Open'),
(2, 'Temporarily Closed');

INSERT INTO location (lid, city, country)
VALUES (1, 'Delhi', 'India'),
(2, 'Bangalore', 'India');

INSERT INTO users (uid, name, username, password)
VALUES (0, 'Admin', 'admin', 'superkey');


'''

QUERY_RES_TEMPLATE = '({}, {}, {}, {}, {}, {}, {}, {}, {}, {})';

# Restaurant data
file_dump += 'INSERT INTO restaurants (id, name, address, phone, website, latitude, longitude, status, location, owner_id)\nVALUES '
restaurants_arr = []
counter = 0
with open(PATH_RES_DATA, 'r') as json_file:
  counter += 1
  res_data = json.load(json_file)
  for data in res_data:
    restaurants_arr.append(QUERY_RES_TEMPLATE.format(
      data['site_code'],
      convert_to_string(data['names'][0]['name']),
      convert_to_string(data['main_address']['full_address']),
      convert_to_string(data['phone_number']['number'] if 'phone_number' in data and 'number' in data['phone_number'] else None),
      convert_to_string(data['home_page'] if 'home_page' in data else None),
      data['display_point']['coordinates']['latitude'],
      data['display_point']['coordinates']['longitude'],
      1,
      1 if 'Delhi' in data['main_address']['full_address'] else 2,
      0
    ))

file_dump += ',\n'.join(restaurants_arr) + ';'

print(file_dump)

with open(PATH_INSERT_QUERY_FILE, 'w') as sql_file:
  sql_file.write(file_dump)