# upshot-take-home-test
This test simulates a data pipeline where your application will ingest data from an API, store the files, transform the data into tabular form and load the data into a relational database. Finally it will export a summary of the data into a CSV file.

## Project Structure

Project structure: 

- app
    - api_result folder (files that have been extracted from the API endpoint)
    - output folder (csv export of a summary of the data)
    - sql
        - create_tables.sql (sql script to create tables)
    - src folder
        - football_data.py (script to ingest data from the football-data api, store the files, transform data, loads data into Postgres)
        - report.py (creates a report and saves it to the output folder)
    - .env (file has to be created to house environmental variables)
    - docker-compose.yml (creates containers for Postgres and execute football_data.py & report.py)
    - Dockerfile_football_data (create container for football pipeline)
    - Dockerfile_report (create container for reporting)
    - requirements.txt (python modules for the project)
- README.md

## Steps for running for the project

Project Prerequisites

- [Docker](https://www.docker.com) (required be installed on your machine in order to run the project)
- Apply for an football-data API Key [here](https://www.football-data.org/client/register).
- Create an .env file inside the app folder

Environmental Variables in the .env file

```python
API_KEY = "" #Place API Key here
API_ENDPOINT = "https://api.football-data.org/v4/"
DB_USERNAME = "postgres" #Replace Defualt Variables - Before Deploying to another ENV
DB_PASSWORD = "postgres"#Replace Defualt Variables - Before Deploying to another ENV
DB_HOST = "host.docker.internal"
DB_NAME = "football"
```

Once Docker has been installed, .env file has been created under the app folder and environmental variables are placed in the .env file. You can now run the application

## Usage

Open a terminal/CMD window and change directory to where football_data_pipeline folder is saved

### Run the following command to start the project

```bash
docker compose -f docker-compose.yml up -d
```
Expectations
- Docker will spin up 3 containers
    1. postgres container will be created
        - Create/Mount a volume for a persistent store
        - Creation of a database named football
            - Create a public Schema
        - The create_tables.sql will run creating the following tables
            - dim_teams
                - id integer NOT NULL
                - name TEXT NOT NULL
                - PRIMARY KEY (id)
            - dim_competitions
                - id integer NOT NULL
                - name TEXT NOT NULL
                - PRIMARY KEY (id)
            - fact_competitions
                - competition_id integer NOT NULL
                - team_id TEXT NOT NULL
                - PRIMARY KEY (competition_id, team_id)

    2. python_football_data container will be created
        - Dependency on the postgres container
        - run after postgres container passes health check
        - the script will ingest data from two API endpoints
            - [competitions](https://api.football-data.org/v4/competitions)
                - id and name will be saved to Postgres table dim_competitions
            - [teams within the competitions](https://api.football-data.org/v4/competitions/%7Bid%7D/teams)
                - team id and name will be saved to Postgres table dim_teams
                 - fact_competitions table data will be generated
        - raw data will be stored in the api_result folder for debugging  
        - load the data into a Postgres database
            - Using sqlalchemy & psycopg2
                - sqlalchemy is used facilitates the communication between Python and Postgres. [Reference](https://www.sqlalchemy.org/)
                - psycopg2 is an adapter for the Python and Postgres. [Reference](https://pypi.org/project/psycopg2/)
            - dim_teams
            - dim_competitions
            - fact_competitions

    3. python_report container will be created
        - Dependency on the python_football_data container
        - automatically run after python_football_data container
        - script will create a summary csv file in the output folder from the data return by the query

### Stop the project
```bash
docker compose -f docker-compose.yml down
```

## Pending Items for Production Readiness
- Before Project can be Deploy to another ENV. The following action items are pending
    - Create a db_conn.py file for Database class with connection and cursor inside.
    - Refactor all current db_connection in  football_data.py and report.py to use the new db_conn.py class.
    - debug the missing team id {2018} that returns an emtpy team array. 
        - not being added as part of the summary report / fact_competitions table
    - Refactor sleep(5) from request to better handle request being sent out
    - Enchance Error handling for API and Postgres
    - create a pull request for code review
    - create a CI/CD
    - setup a workflow
      - e.g. github actions
        - triggers the workflow
            - push or pull request events for "main" branch only
            - build the docker containers
            - deploy the docker containers to the cloud (e.g AWS)
    - move variables from .env to a param store 
    - create external volumes for docker container
    - Remove deflaut passwords
    - Change Database Script to create a private schema instead of using the default public schema
    - modify docker-compose file to appropriate volumes and env variables
    - Creation of an ECS-Cluster
    - Add observability (e.g. AWS CloudWatch LOG)
    - Add a persistent layer to the cluster