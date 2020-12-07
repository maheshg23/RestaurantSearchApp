import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser

'# RESTAURANT SEARCH APPLICATION'

@st.cache
def get_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

def is_valid_val(v):
    return v and v != 'None'

def get_unique(arr):
    t = set(arr)
    return [x for x in arr if x in t]

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

    query = 'SELECT'

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
    
    query = 'SELECT {} FROM {}'.format(', '.join(get_unique(query_cols)), ', '.join(get_unique(query_from)))
    if query_where:
        query = '{} WHERE {}'.format(query, ' AND '.join(get_unique(query_where)))
    
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

db_query1 = f"""SELECT ROUND(avg_rating, 3) as average_rating, * FROM restaurants JOIN ( 
                SELECT res_id, avg(rating) AS avg_rating FROM reviews 
                GROUP BY res_id 
            ) AS reviews 
            ON restaurants.id = reviews.res_id 
            ORDER BY average_rating DESC 
            LIMIT 5;"""

df = query_db(db_query1)
st.dataframe(df)

'## Query 2 - Photos and Reviews'
'### List all reviews and photos posted for each restaurant along with the username who posted it' 

tables_to_sel = ['reviews', 'photos']
table_sel = st.radio('Choose Review or Photos', tables_to_sel)

sql_restaurant_names = 'SELECT name FROM restaurants;'
restaurant_names = query_db(sql_restaurant_names)['name'].tolist()
restaurant_names.insert(0, "All")
restaurant_name = st.selectbox('Choose a Restaurant:', restaurant_names)

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

df = query_db(db_sql_query)
st.dataframe(df)


'## Query 3'
'### Search with Restaurant Name, City, Country, Status, Tags, Payment Method'

# search_key = ['Restaurant Name','City','Country','Status','Tags','Payment Method']
# search_sel = st.radio('Choose a Search', search_key)
# if search_sel == 'Restaurant Name':
sql_restaurant_names = 'SELECT name FROM restaurants;'
restaurant_names = query_db(sql_restaurant_names)['name'].tolist()
restaurant_names.insert(0, "None")
restaurant_name = st.selectbox('Choose a Restaurant', restaurant_names)
    
# if search_sel == 'City':
sql_cities = 'SELECT DISTINCT city FROM location;'
cities = query_db(sql_cities)['city'].tolist()
cities.insert(0, "None")
city = st.selectbox(f'Choose a City', cities)

# if search_sel == 'Country':
sql_countries = 'SELECT DISTINCT country FROM location;'
countries = query_db(sql_countries)['country'].tolist()
countries.insert(0, "None")
country = st.selectbox(f'Choose a Country', countries)

# if search_sel == 'Status':
sql_statuses = 'SELECT DISTINCT name FROM status;'
statuses = query_db(sql_statuses)['name'].tolist()
statuses.insert(0, "None")
status = st.selectbox(f'Choose a Status', statuses)

# if search_sel == 'Tags':
sql_tag_names = 'SELECT DISTINCT name FROM tags;'
tags_list = query_db(sql_tag_names)['name'].tolist()
# tags_list.insert(0, "None")
# tag = st.selectbox(f'Choose a Tag', tags)
tags = st.multiselect('Choose different Tags', tags_list)

# if search_sel == 'Payment Method':
sql_payment_methods = 'SELECT DISTINCT name FROM payment_methods;'
payment_methods = query_db(sql_payment_methods)['name'].tolist()
payment_methods.insert(0, "None")
payment_method = st.selectbox(f'Choose a Payment Method', payment_methods)


# search_list_sel = st.selectbox(f'Choose a {search_sel}', search_list)

# country_sel = st.radio('Choose a Country', countries)
# city_sel = st.radio('Choose a City', cities)
# tag_name_sel = st.selectbox('Choose an Restaurant Tag', tag_names)
# status_sel = st.selectbox('Choose an Restaurant Status', statuses)
# payment_method_sel = st.selectbox('Choose an Restaurant Status', payment_methods)
db_query = parse_query3(restaurant_name, city, country, status, tags, payment_method)

df = query_db(db_query)
st.dataframe(df)
# st.dataframe(df,2000,1000)

# if country_sel: 
#     db_query = f""" SELECT * FROM restaurants AS res, status AS s, location AS l, restaurant_payments_mapping AS rpm, payment_methods AS pm
#                     where   res.status = s.sid AND 
#                             res.location = l.lid AND 
#                             res.id = rpm.res_id AND 
#                             rpm.payment_id = pm.pmid AND 
#                             l.country = '{country_sel}';"""                  
#     df = query_db(db_query)
#     st.dataframe(df)

# if city_sel: 
#     db_query = f""" SELECT * FROM restaurants AS res, status AS s, location AS l, restaurant_payments_mapping AS rpm, payment_methods AS pm
#                     where   res.status = s.sid AND 
#                             res.location = l.lid AND 
#                             res.id = rpm.res_id AND 
#                             rpm.payment_id = pm.pmid AND 
#                             l.city = '{city_sel}';"""              
#     df = query_db(db_query)
#     st.dataframe(df)



# '## Query Restaurants'

# sql_restaurant_names = 'select name from restaurants;'
# restaurant_names = query_db(sql_restaurant_names)['name'].tolist()
# restaurant_name = st.selectbox('Choose a Restaurant', restaurant_names)
# if restaurant_name:
#     sql_restaurant = f"select * from restaurants where name = '{restaurant_name}';"
#     customer_info = query_db(sql_restaurant).loc[0]
#     c_address, c_city, c_state = customer_info['address'], customer_info['phone'], customer_info['owner_id']
#     st.write(f"{customer_name} is at {c_address}, and contact in {customer_info['phone']}, {customer_info['owner_id']}.")


# '## Demo Query customers'

# sql_customer_names = 'select name from customers;'
# customer_names = query_db(sql_customer_names)['name'].tolist()
# customer_name = st.selectbox('Choose a customer', customer_names)
# if customer_name:
#     sql_customer = f"select * from customers where name = '{customer_name}';"
#     customer_info = query_db(sql_customer).loc[0]
#     c_age, c_city, c_state = customer_info['age'], customer_info['city'], customer_info['state']
#     st.write(f"{customer_name} is {c_age}-year old, and lives in {customer_info['city']}, {customer_info['state']}.")


# '## Demo Query orders'

# sql_order_ids = 'select order_id from orders;'
# order_ids = query_db(sql_order_ids)['order_id'].tolist()
# order_id = st.selectbox('Choose an order', order_ids)
# if order_id:
#     sql_order = f"""select C.name, O.order_date
#                     from orders as O, customers as C 
#                     where O.order_id = {order_id}
#                     and O.customer_id = C.id;"""
#     customer_info = query_db(sql_order).loc[0]
#     customer_name = customer_info['name']
#     order_date = customer_info['order_date']
#     st.write(f'This order is placed by {customer_name} on {order_date}.')


# '## Demo List the customers by city'
# sql_cities = 'select distinct city from customers;'
# cities = query_db(sql_cities)['city'].tolist()
# city_sel = st.radio('choose a city', cities)
# if(city_sel):
#     sql_customers = f"select name from customers where city = '{city_sel}' order by name;"
#     customer_names = query_db(sql_customers)['name'].tolist()
#     customer_names_str = '\n\n'.join([str(elm) for elm in customer_names])
#     st.write(f"The Below customers live in the city '{city_sel}'\n\n {customer_names_str}")


# '## Demo List the orders by customers '
# sql_customers_info = 'select id, name from customers;'
# cust_info = query_db(sql_customers_info)
# cust_ids,cust_names = cust_info['id'].tolist(),cust_info['name'].tolist()

# cust_id_names = [a + ' : ' + str(b) for a,b in zip(cust_names, cust_ids)]

# customer_name = st.multiselect('Choose customers (Customer Name : Customer ID) to look for their Orders.', cust_id_names)
# if(customer_name):
#     customer_id = [a.split(':')[1].strip() for a in customer_name]
#     customer_id_str = ','.join([str(elm) for elm in customer_id])

#     sql_orders = f"""select C.name, O.order_id, O.order_date, O.order_amount
#                     from orders as O, customers as C
#                     where O.customer_id in ({customer_id_str})
#                     and O.customer_id = c.id;"""
    
#     df_order_info = query_db(sql_orders)
#     if(not df_order_info.empty):
#         st.dataframe(df_order_info)
#     else:
#         st.write('No Orders.')
