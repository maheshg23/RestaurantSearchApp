import os
import json
import string
import random
from datetime import datetime

FILENAME_ROOT = './'
FILENAME_RES_DATA = 'res_sample.json'
FILENAME_RES_PHOTOS_DATA = 'photo_sample.json'
FILENAME_INSERT_QUERIES = 'load.sql'

TABLES_WITH_PROPERTIES = {
  'tags': ['tid', 'name'],
  'location': ['lid', 'city', 'country'],
  'restaurant_tags_mapping': ['res_id', 'tag_id'],
  'users': ['uid', 'name', 'username', 'password'],
  'restaurant_payments_mapping': ['res_id', 'payment_id'],
  'photos': ['pid', 'url', 'timestamp', 'user_id', 'res_id'],
  'reviews': ['rid', 'text', 'rating', 'timestamp', 'user_id', 'res_id'],
  'restaurants': ['id', 'name', 'address', 'phone', 'website', 'latitude', 'longitude', 'status', 'location', 'owner_id']
}

def get_data_file_path(filename):
  return os.path.join(FILENAME_ROOT, filename)

def convert_to_string(param):
  return '\'{}\''.format(param.replace("'", "''")) if param else 'NULL'

def get_query_value_template(n):
  if n:
    return '({})'.format(('{}, ' * n)[:-2])
  return ''

def array_to_query(arr, separator = ',\n'):
  if arr:
    return separator.join(arr) + ';\n\n'
  return '';

def get_query_initial(tablename):
  if tablename and tablename in TABLES_WITH_PROPERTIES:
    return 'INSERT INTO {} ({})\nVALUES '.format(tablename, ', '.join(TABLES_WITH_PROPERTIES[tablename]))
  return ''

def format_timestamp(t):
  return 'timestamp \'{}\''.format(t)

def remove_multiple_spaces(s):
  return " ".join(s.split())

def get_user_id(s):
  return s.replace("!@#$%^&*()[]{};:,./<>?\|`~-=_+", "").replace(' ', '_').lower()

def get_random_text(N):
  return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

def get_weighted_random_number(upper_limit, percent_of_non_default = 10, default = 0):
  random.seed(datetime.now())
  r = random.choice([i for i in range(1, upper_limit + 1) if i not in [default]])
  dataset = [default] * (100 - percent_of_non_default) + [r] * percent_of_non_default 
  return random.choice(dataset)

def get_location_data():
  in_cities = ['Delhi', 'Mumbai', 'Pune', 'Kolkata']
  au_cities = ['Sydney', 'Melbourne', 'Brisbane']
  cities = in_cities + au_cities
  countries = ['India'] * len(in_cities) + ['Australia'] * len(au_cities)
  return cities, countries

def get_location_id(s):
  cities, _ = get_location_data()
  for i in range(len(cities)):
    c = cities[i]
    if c in s:
      return i + 1

PATH_RES_DATA = get_data_file_path(FILENAME_RES_DATA)
PATH_PHOTOS_REVIEWS_DATA = get_data_file_path(FILENAME_RES_PHOTOS_DATA)
PATH_INSERT_QUERY_FILE = get_data_file_path(FILENAME_INSERT_QUERIES)

QUERY_TEMPLATE_2 = get_query_value_template(2)
QUERY_TEMPLATE_3 = get_query_value_template(3)
QUERY_TEMPLATE_4 = get_query_value_template(4)
QUERY_TEMPLATE_5 = get_query_value_template(5)
QUERY_TEMPLATE_6 = get_query_value_template(6)
QUERY_TEMPLATE_10 = get_query_value_template(10)

file_dump = '''INSERT INTO status (sid, name)
VALUES (1, 'Closed'),
(2, 'Open'),
(3, 'Temporarily Closed');

INSERT INTO payment_methods (pmid, name)
VALUES (1, 'Cash'),
(2, 'Credit Card'),
(3, 'Debit Card');

'''


cities, countries = get_location_data()

query_location = []
for i in range(len(cities)):
  query_location.append(QUERY_TEMPLATE_3.format(
    i + 1,
    convert_to_string(cities[i]),
    convert_to_string(countries[i])
  ))

# Restaurant data
query_restaurants = []
query_tags = []
query_payments = []
query_res_tags_mapping = []
selected_tags = {}

skip_tags = ['credit-card', 'cash', 'debit_card', 'wallet-accepted',]

# photos
query_photos = []
query_reviews = []

# users
query_users = [
  "(0, 'Admin', 'admin', 'superkey')"
]
res_list = []
username_userid_map = {}

counter_photos = 0
counter_reviews = 0
counter_users = 0

with open(PATH_PHOTOS_REVIEWS_DATA, 'r') as json_file:
  d = json.load(json_file)
  for data in d:
    res_id = data['site_code']
    if 'reviews' in data:
      for review in data['reviews']:
        user_name =remove_multiple_spaces(review['user']['profile_name'])
        username = get_user_id(user_name)
        if username not in username_userid_map:
          counter_users += 1
          username_userid_map[username] = counter_users
          query_users.append(QUERY_TEMPLATE_4.format(
            counter_users,
            convert_to_string(user_name),
            convert_to_string(username),
            convert_to_string(get_random_text(12))
          ))

      for review in data['reviews']:
        counter_reviews += 1
        user_name = remove_multiple_spaces(review['user']['profile_name'])
        username = get_user_id(user_name)
        query_reviews.append(QUERY_TEMPLATE_6.format(
          counter_reviews,
          convert_to_string(review['review']['text'][:2000]),
          review['score'],
          format_timestamp(review['date_added']),
          username_userid_map[username],
          res_id
        ))

    for photo in data['photos']:
      counter_photos += 1
      query_photos.append(QUERY_TEMPLATE_5.format(
        counter_photos,
        convert_to_string(photo['photo_sizes']['original']['url']),
        format_timestamp(photo['date_added']),
        get_weighted_random_number(counter_users),
        res_id
      ))

with open(PATH_RES_DATA, 'r') as json_file:
  res_data = json.load(json_file)
  for data in res_data:
    res_id = data['site_code']
    res_list.append(res_id)
    owner = get_weighted_random_number(counter_users, 20)
    query_restaurants.append(QUERY_TEMPLATE_10.format(
      res_id,
      convert_to_string(data['names'][0]['name']),
      convert_to_string(data['main_address']['full_address']),
      convert_to_string(data['phone_number']['number'] if 'phone_number' in data and 'number' in data['phone_number'] else None),
      convert_to_string(data['home_page'] if 'home_page' in data else None),
      data['display_point']['coordinates']['latitude'],
      data['display_point']['coordinates']['longitude'],
      get_weighted_random_number(3, 10, 2),
      get_location_id(data['main_address']['full_address']),
      owner
    ))
    query_payments.append(QUERY_TEMPLATE_2.format(
      res_id,
      1
    ))

    for key, value in data['attributes'].items():
      if key not in skip_tags:
        if key not in selected_tags:
          selected_tags[key] = value['attribute_id']
          query_tags.append(QUERY_TEMPLATE_2.format(
            value['attribute_id'],
            convert_to_string(value['attribute_name'])
          ))
        query_res_tags_mapping.append(QUERY_TEMPLATE_2.format(
          res_id,
          selected_tags[key]
        ))
      elif 'credit' in key or 'debit' in key:
        query_payments.append(QUERY_TEMPLATE_2.format(
          res_id,
          2 if 'credit' in key else 3
        ))

file_dump += get_query_initial('location') + array_to_query(query_location)
file_dump += get_query_initial('users') + array_to_query(query_users)
file_dump += get_query_initial('restaurants') + array_to_query(query_restaurants)
file_dump += get_query_initial('tags') + array_to_query(query_tags)
file_dump += get_query_initial('restaurant_tags_mapping') + array_to_query(query_res_tags_mapping)
file_dump += get_query_initial('restaurant_payments_mapping') + array_to_query(query_payments)

file_dump += get_query_initial('photos') + array_to_query(query_photos)
file_dump += get_query_initial('reviews') + array_to_query(query_reviews)

with open(PATH_INSERT_QUERY_FILE, 'w') as sql_file:
  sql_file.write(file_dump)

print('Created {}'.format(FILENAME_INSERT_QUERIES))