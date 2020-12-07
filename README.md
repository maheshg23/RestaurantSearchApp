# RestaurantSearchApp
Principal of Database Systems Project - Restaurant Search and Discovery Platform Application

### Export NYU net id, univ id and port number

```bash
export USER_ID=mg6233
export NYU_ID=
export PORT=8567
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