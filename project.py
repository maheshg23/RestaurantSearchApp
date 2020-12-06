import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser

'# Demo: Streamlit + Postgres'

@st.cache
def get_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


@st.cache
def query_db(sql: str):
    # print(f'Running query_db(): {sql}')

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


'## Read tables'

sql_all_table_names = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
all_table_names = query_db(sql_all_table_names)['relname'].tolist()
table_name = st.selectbox('Choose a table', all_table_names)
if table_name:
    f'Display the table'

    sql_table = f'select * from {table_name};'
    df = query_db(sql_table)
    st.dataframe(df)

'## Query 1 - List the top 5 restaurants based on the average user reviews'

db_query1 = f"""SELECT avg_rating,* FROM restaurants JOIN ( 
                SELECT res_id, avg(rating) AS avg_rating FROM reviews 
                GROUP BY res_id 
            ) AS reviews 
            ON restaurants.id = reviews.res_id 
            ORDER BY avg_rating DESC 
            LIMIT 5;"""

df = query_db(db_query1)
st.dataframe(df)

'## Query 2 - Photos and Reviews'
'## List all reviews and photos posted for each restaurant along with the username who posted it' 

tables_to_sel = ['reviews', 'photos']
table_sel = st.radio('choose Review or Photos', tables_to_sel)

sql_restaurant_names = 'select name from restaurants;'
restaurant_names = query_db(sql_restaurant_names)['name'].tolist()
restaurant_names.insert(0, "All")
restaurant_name = st.selectbox('Choose a Restaurant', restaurant_names)

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
    db_sql_query = f""" SELECT res.id, res.name, p.pid, p.url, u.uid, u.username 
                        FROM restaurants AS res, photos AS p, users AS u 
                        WHERE res.id = p.res_id AND u.uid = p.user_id and res.name = '{restaurant_name}'
                        ORDER BY res.id;"""

df = query_db(db_sql_query)
st.dataframe(df)




'## Demo Select Orders' 

sql_order_ids = 'select order_id from orders;'
order_ids = query_db(sql_order_ids)['order_id'].tolist()
order_id = st.selectbox('Choose an order', order_ids)
if order_id:
    sql_order = f"""select C.name, O.order_date
                    from orders as O, customers as C 
                    where O.order_id = {order_id}
                    and O.customer_id = C.id;"""

    customer_info = query_db(sql_order).loc[0]
    customer_name = customer_info['name']
    order_date = customer_info['order_date']
    st.write(f'This order is placed by {customer_name} on {order_date}.')


'## Query Restaurants'

sql_restaurant_names = 'select name from restaurants;'
restaurant_names = query_db(sql_restaurant_names)['name'].tolist()
restaurant_name = st.selectbox('Choose a Restaurant', restaurant_names)
if restaurant_name:
    sql_restaurant = f"select * from restaurants where name = '{restaurant_name}';"
    customer_info = query_db(sql_restaurant).loc[0]
    c_address, c_city, c_state = customer_info['address'], customer_info['phone'], customer_info['owner_id']
    st.write(f"{customer_name} is at {c_address}, and contact in {customer_info['phone']}, {customer_info['owner_id']}.")


'## Demo Query customers'

sql_customer_names = 'select name from customers;'
customer_names = query_db(sql_customer_names)['name'].tolist()
customer_name = st.selectbox('Choose a customer', customer_names)
if customer_name:
    sql_customer = f"select * from customers where name = '{customer_name}';"
    customer_info = query_db(sql_customer).loc[0]
    c_age, c_city, c_state = customer_info['age'], customer_info['city'], customer_info['state']
    st.write(f"{customer_name} is {c_age}-year old, and lives in {customer_info['city']}, {customer_info['state']}.")


'## Demo Query orders'

sql_order_ids = 'select order_id from orders;'
order_ids = query_db(sql_order_ids)['order_id'].tolist()
order_id = st.selectbox('Choose an order', order_ids)
if order_id:
    sql_order = f"""select C.name, O.order_date
                    from orders as O, customers as C 
                    where O.order_id = {order_id}
                    and O.customer_id = C.id;"""
    customer_info = query_db(sql_order).loc[0]
    customer_name = customer_info['name']
    order_date = customer_info['order_date']
    st.write(f'This order is placed by {customer_name} on {order_date}.')


'## Demo List the customers by city'
sql_cities = 'select distinct city from customers;'
cities = query_db(sql_cities)['city'].tolist()
city_sel = st.radio('choose a city', cities)
if(city_sel):
    sql_customers = f"select name from customers where city = '{city_sel}' order by name;"
    customer_names = query_db(sql_customers)['name'].tolist()
    customer_names_str = '\n\n'.join([str(elm) for elm in customer_names])
    st.write(f"The Below customers live in the city '{city_sel}'\n\n {customer_names_str}")


'## Demo List the orders by customers '
sql_customers_info = 'select id, name from customers;'
cust_info = query_db(sql_customers_info)
cust_ids,cust_names = cust_info['id'].tolist(),cust_info['name'].tolist()

cust_id_names = [a + ' : ' + str(b) for a,b in zip(cust_names, cust_ids)]

customer_name = st.multiselect('Choose customers (Customer Name : Customer ID) to look for their Orders.', cust_id_names)
if(customer_name):
    customer_id = [a.split(':')[1].strip() for a in customer_name]
    customer_id_str = ','.join([str(elm) for elm in customer_id])

    sql_orders = f"""select C.name, O.order_id, O.order_date, O.order_amount
                    from orders as O, customers as C
                    where O.customer_id in ({customer_id_str})
                    and O.customer_id = c.id;"""
    
    df_order_info = query_db(sql_orders)
    if(not df_order_info.empty):
        st.dataframe(df_order_info)
    else:
        st.write('No Orders.')
