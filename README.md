# 0L-log-indexer
Toolset to index log entries from n number of 0L validator log files based upon a series of time ranges.

## Prerequisites
1. Have docker installed properly.
2. Have the requirements installed:
```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```
## Spin up a postgres db
First pull the latest postgres image:
```bash
docker pull postgres
```
Run the image:
```bash
docker run\
    --name researchDB\
    -p 5432:5432\
    -e POSTGRES_USER=research\
    -e POSTGRES_PASSWORD=research\
    -e POSTGRES_DB=research\
    -d postgres
```
## Start indexing log files
1. Check if the db is receiving connections:
```bash
docker logs researchDB
```
2. Define the desired configurations in config.py
3. Run app.py
## Some docker commands that might come in handy...
Get into the the container shell:
```bash
docker exec -it researchDB /bin/bash
```
Enter the db container to make queries directly on db:
```bash
docker exec -it ol-intel-db /bin/bash
/ # su postgres
/ $ psql postgresql://research:research@localhost:5432/research
...
research=# select _json from validatorlog where _json->>'name' = 'progress_check';
...
research=# exit
/ $ exit
/ # exit
```
Take down the container (and lose all data in it):
```bash
docker rm -f researchDB
```
## Some other commands that might come in handy:
Create a db dump:
```bash
docker exec -t researchDB pg_dumpall -c -U research | gzip > ./assets/db_dumps/dump_all.gz
```
Restore a db dump:
```bash
gunzip < ./assets/db_dumps/dump_all.gz | docker exec -i researchDB psql -U research -d research
```
In postgres, one can access json elements inside a JSONB field by using the -> and/or --> operator:
![JSONB example](assets/images/_json.png)
## TODOs
1. Optimize recurring code
2. Make test async, if possible
3. Remove code blocks never visited, if any
4. Add date regex generator
