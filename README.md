# RestaurantSearchApp
## Principal of Database Systems Project - Restaurant Search and Discovery Platform Application
  
This application will serve as a database of restaurants using which users can search for specific restaurants based on some filters. Users can also view details of the retaurants including address, owner, ratings, reviews, and photos which will help them to select their preferred restaurants.    
   
   
    
### Export NYU net id, univ id and port number

```bash
export USER_ID=mg6233
export NYU_ID=
export PORT=8579
```


### Change directory to data, generate load.sql and sync with gauss server

```bash
cd RestaurantSearchApp/data
python3 load.py && sshpass -p $NYU_ID rsync -avz ../ "$USER_ID@gauss.poly.edu:/home/$USER_ID/project"
```


### SSH to gauss and connect the port to localhost

```bash
sshpass -p $NYU_ID ssh -L "$PORT":localhost:"$PORT" "$USER_ID@gauss.poly.edu"
```

### Import schema and data
```bash
export USER_ID=mg6233
export PORT=8567
cd project

psql -d "$USER_ID-db" -a -f code/schema.sql
psql -d "$USER_ID-db" -a -f data/load.sql
```

### Run Streamlite App 
```
streamlit run code/project.py --server.address=localhost --server.port=$PORT
```

### Connect to database

```bash
psql -h localhost -U $USER_ID "$USER_ID-db"
```

### Run in background
```bash
tmux new -d -s mySession
tmux send-keys -t mySession.0 "cd /home/$USER_ID/project && streamlit run code/project.py --server.address=localhost --server.port=$PORT" ENTER
```
to exit the tmux 
Press CTRL + B, then D

### References 
- https://share.streamlit.io/daniellewisdl/streamlit-cheat-sheet/app.py
- https://docs.streamlit.io/en/0.64.0/api.html