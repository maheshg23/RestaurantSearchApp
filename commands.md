
### User specific Commands
```bash

ssh -L 8579:localhost:8579 mg6233@gauss.poly.edu

psql -h localhost -U mg6233 mg6233-db

psql -d mg6233-db -a -f code/schema.sql
psql -d mg6233-db -a -f data/load.sql

streamlit run code/project.py --server.address=localhost --server.port=8579

```
