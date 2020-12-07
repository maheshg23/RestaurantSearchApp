# RestaurantSearchApp
Principal of Database Systems Project - Restaurant Search and Discovery Platform Application


Load the schema.sql life using the below command 

psql -d mg6233-db -a -f PDSRestaurantSearchApp/schema.sql

Run Streamlite App 
streamlit run project.py --server.address=localhost --server.port=8579
streamlit run code/project.py --server.address=localhost --server.port=8579

run plsql command promt 
psql -h localhost -U mg6233 mg6233-db

ssh mg6233@gauss.poly.edu 

ssh -L 8579:localhost:8579 mg6233@gauss.poly.edu

load file into gauss
python3 load.py && sshpass -p $NYU_ID rsync -avz ./ pa1432@gauss.poly.edu:/home/pa1432/project