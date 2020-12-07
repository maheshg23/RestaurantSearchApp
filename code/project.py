import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser
from collections import OrderedDict

'# RESTAURANT SEARCH APPLICATION'

@st.cache
def get_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

def is_valid_val(v):
    return v and v != 'None'

def get_unique(arr):
    return list(OrderedDict.fromkeys(arr))

def parse_query3(res_name, city, country, status, tags, payment_method):
    query_parts = {
        'name': {
            'cols': [],
            'where_param': 'r.name = \'{}\''
        },
        'city': {
            'cols': ['l.lid AS location_id', 'l.city'],
            'from': 'location l',
            'where': 'l.lid = r.location',
            'where_param': 'l.city = \'{}\''
        },
        'country': {
            'cols': ['l.lid AS location_id', 'l.country'],
            'from': 'location l',
            'where': 'l.lid = r.location',
            'where_param': 'l.country = \'{}\''
        },
        'status': {
            'cols': ['s.sid AS status_id', 's.name AS status'],
            'from': 'status s',
            'where': 'r.status = s.sid',
            'where_param': 's.name = \'{}\''
        },
        'tags': {
            'cols': ['t.tid AS tag_id', 't.name AS tag'],
            'from': 'tags t, restaurant_tags_mapping tm',
            'where_param': 't.tid = tm.tag_id AND t.name IN ({}) AND r.id = tm.res_id'
        },
        'payment_method': {
            'cols': ['p.pmid AS payment_id', 'p.name AS payment_method'],
            'from': 'payment_methods p, restaurant_payments_mapping pm',
            'where': 'p.pmid = pm.payment_id',
            'where_param': 'p.name = \'{}\''
        }
    }

    query_cols = ['DISTINCT r.id AS res_id', 'r.name', 'r.address', 'r.phone', 'r.website', 'r.latitude', 'r.longitude', 'r.status', 'r.location', 'r.owner_id']
    query_from = ['restaurants r']
    query_where = []

    def parse_query_part(k, val):
        c, f, w = [], '', []
        if is_valid_val(val) and k in query_parts:
            v = val if k != 'tags' else ', '.join(["\'{}\'".format(i) for i in val])
            d = query_parts[k]
            c = d['cols']
            f = d['from'] if 'from' in d else ''
            if 'where' in d:
                w.append(d['where'])
            if 'where_param' in d:
                w.append(d['where_param'].format(v))
        return c, f, w

    keys = list(query_parts.keys())
    vals = [res_name, city, country, status, tags, payment_method]
    for i in range(len(keys)):
        val = vals[i] if isinstance(vals[i], list) else vals[i].replace("'", "''")
        c, f, w = parse_query_part(keys[i], val)
        query_cols += c
        if f:
            query_from.append(f)
        if w:
            query_where += w
    
    query = """ SELECT {} 
                FROM {}""".format(', '.join(get_unique(query_cols)), ', '.join(get_unique(query_from)))
    if query_where:
        query = """{} 
                WHERE {}""".format(query, ' AND '.join(get_unique(query_where)))
    
    return '{};'.format(query)


@st.cache
def query_db(sql: str):
    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Obtain data
    data = cur.fetchall()
    
    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df

'## Display Tables'

sql_all_table_names = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';"
all_table_names = query_db(sql_all_table_names)['relname'].tolist()
table_name = st.selectbox('Choose a table', all_table_names)
if table_name:
    f'Display All Table Infromation'
    sql_table = f'SELECT * FROM {table_name};'
    df = query_db(sql_table)
    st.dataframe(df)

'## Query 1'
'### List the top 5 restaurants based on the average user reviews'

db_query1 = f"""SELECT res.id, res.name, avg_rating 
                FROM restaurants as res JOIN 
                    (   SELECT res_id, ROUND(avg(rating),3) AS avg_rating FROM reviews 
                        GROUP BY res_id 
                    ) AS reviews_rating 
                ON res.id = reviews_rating.res_id 
                ORDER BY reviews_rating.avg_rating DESC 
                LIMIT 5;"""

'#### Query'
st.code(db_query1)

'#### Result'
df = query_db(db_query1)
st.dataframe(df)

'## Query 2'
'### List all reviews and photos posted for each restaurant along with the username who posted it' 

tables_to_sel = ['reviews', 'photos']
table_sel = st.radio('Choose Review or Photos', tables_to_sel)

sql_restaurant_names = 'SELECT name FROM restaurants;'
restaurant_names = query_db(sql_restaurant_names)['name'].tolist()
restaurant_names.insert(0, "All")
restaurant_name = st.selectbox('Choose a Restaurant:', restaurant_names)
restaurant_name = restaurant_name.replace("'","''")

if table_sel == 'reviews':
    if (restaurant_name == 'All'):
        db_sql_query = f""" SELECT res.id, res.name, r.rid, r.text, u.uid, u.username  
                        FROM restaurants AS res, reviews AS r, users AS u 
                        WHERE res.id = r.res_id and u.uid = r.user_id
                        ORDER BY res.id;"""
    else:
        db_sql_query = f""" SELECT res.id, res.name, r.rid, r.text, u.uid, u.username  
                        FROM restaurants AS res, reviews AS r, users AS u 
                        WHERE res.id = r.res_id and u.uid = r.user_id and res.name = '{restaurant_name}'
                        ORDER BY res.id;"""
else:
    if (restaurant_name == 'All'):
        db_sql_query = f""" SELECT res.id, res.name, p.pid, p.url, u.uid, u.username 
                            FROM restaurants AS res, photos AS p, users AS u 
                            WHERE res.id = p.res_id AND u.uid = p.user_id 
                            ORDER BY res.id;"""
    else:                    
        db_sql_query = f""" SELECT res.id, res.name, p.pid, p.url, u.uid, u.username 
                            FROM restaurants AS res, photos AS p, users AS u 
                            WHERE res.id = p.res_id AND u.uid = p.user_id and res.name = '{restaurant_name}'
                            ORDER BY res.id;"""
'#### Query'
st.code(db_sql_query)

'#### Result'
df = query_db(db_sql_query)
st.dataframe(df)


'## Query 3'
'### Search with Restaurant Name, City, Country, Status, Tags, Payment Method'

sql_restaurant_names = 'SELECT name FROM restaurants;'
restaurant_names = query_db(sql_restaurant_names)['name'].tolist()
restaurant_names.insert(0, "None")
restaurant_name = st.selectbox('Choose a Restaurant', restaurant_names)
restaurant_name = restaurant_name.replace("'","''")

sql_cities = 'SELECT DISTINCT city FROM location;'
cities = query_db(sql_cities)['city'].tolist()
cities.insert(0, "None")
city = st.selectbox(f'Choose a City', cities)

sql_countries = 'SELECT DISTINCT country FROM location;'
countries = query_db(sql_countries)['country'].tolist()
countries.insert(0, "None")
country = st.selectbox(f'Choose a Country', countries)

sql_statuses = 'SELECT DISTINCT name FROM status;'
statuses = query_db(sql_statuses)['name'].tolist()
statuses.insert(0, "None")
status = st.selectbox(f'Choose a Status', statuses)

sql_tag_names = 'SELECT DISTINCT name FROM tags;'
tags_list = query_db(sql_tag_names)['name'].tolist()
tags = st.multiselect('Choose different Tags', tags_list)

sql_payment_methods = 'SELECT DISTINCT name FROM payment_methods;'
payment_methods = query_db(sql_payment_methods)['name'].tolist()
payment_methods.insert(0, "None")
payment_method = st.selectbox(f'Choose a Payment Method', payment_methods)

db_query = parse_query3(restaurant_name, city, country, status, tags, payment_method)

'#### Query'
st.code(db_query)

df = query_db(db_query)
st.dataframe(df)
# st.dataframe(df,2000,1000)

'## Query 4 '
'### Show 10 users with the maximum number of reviews posted by them'


db_query_4 = """SELECT u.uid, u.name, u.username, reviews_user.review_count 
                FROM users AS u, 
                    (   SELECT user_id, COUNT(*) as review_count
                        FROM reviews 
                        GROUP BY user_id
                    ) AS reviews_user
                WHERE u.uid = reviews_user.user_id 
                ORDER BY review_count DESC 
                LIMIT 10;"""

'#### Query'
st.code(db_query_4)

'#### Result'
df = query_db(db_query_4)
st.dataframe(df)


'## Query 5 '
'### Show the Restaurant Owners who give reviews to their own restaurants'


db_query_5 = """SELECT d.rid, d.res_name, d.user_id, d.rating, * 
                FROM users u, 
                    (   SELECT r.id AS rid, r.name AS res_name, r.owner_id AS user_id, AVG(rv.rating) AS rating 
                        FROM restaurants r, reviews rv 
                        WHERE r.id = rv.res_id AND r.owner_id = rv.user_id 
                        GROUP BY r.owner_id, r.id
                    ) d 
                WHERE d.user_id = u.uid;"""

'#### Query'
st.code(db_query_5)

'#### Result'
df = query_db(db_query_5)
st.dataframe(df)


'## Query 6 '
'### List the users who have posted both photos and reviews along with the count of the number of photos and reviews posted by them'


db_query_6 = """SELECT u.uid, u.name, COUNT(DISTINCT rv.rid) AS review_count, COUNT(DISTINCT p.pid) AS photo_count 
                FROM users u, reviews rv, photos p 
                WHERE u.uid = rv.user_id AND u.uid = p.user_id 
                GROUP BY u.uid 
                ORDER BY review_count, photo_count DESC;"""

'#### Query'
st.code(db_query_6)

'#### Result'
df = query_db(db_query_6)
st.dataframe(df)

