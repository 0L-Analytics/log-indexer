# log-indexer
Code to index log entries from n number of 0L validator log files based upon a series of time ranges.

## Prerequisites
1. Have docker installed properly
2. Have the requirements installed
```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```
## Spin up a postgres db
First pull the latest postgres image:
```bash
docker pull postgress
```
Run the image:
```bash
docker run
    --name researchDB
    -p 5455:5432
    -e POSTGRES_USER=research
    -e POSTGRES_PASSWORD=research
    -e POSTGRES_DB=research
    -d
    postgres
```
## Some commands that come in handy...
Get into the the container shell:
```bash
docker exec -it researchDB /bin/bash
```
Take down the container (and lose all data in it):
```bash
docker rm -f researchDB
```
Enter the db container to make queries directly on db:
```bash
docker exec -it ol-intel-db /bin/bash
/ # su postgres
/ $ psql <entire content of DATABASE_URL variable config.py file>
...
research=# select tx->'script'->>'function_name' from foo where bar <> 'ABC';
...
research=# exit
/ $ exit
/ # exit
```
## Start indexing log files
1. Make sure the database is up and running.
2. Check out config.py to set all the configurations.
3. Make sure the log files are in the correct folder, as defined in config.py
4. ...

## TODOs
1. Optimize recurring code
2. Make test async, if possible
3. Remove code blocks never visited, if any
4. Add date regex generator