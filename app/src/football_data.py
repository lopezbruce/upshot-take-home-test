import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import logging
import traceback
import json
import requests
import time

API_KEY = "d0cad9cfa5974747acd4c5603e4ba8bd"
API_ENDPOINT = "https://api.football-data.org/v4/"


def get_football_data_api(URI, result,):
    try:
        logging.info('----get football data from football-data.org----')
        r = requests.get(API_ENDPOINT+URI, headers={'X-Auth-Token': API_KEY})
        if r.status_code == 200:
            return r.json()[result]
        else:
            raise Exception(
                'football data API status code 200 != ' + str(r.status_code))
    except Exception as e:
        logging.error('There is issue with football data url! ' + str(e))
        raise Exception(e)


def postgres_upsert(table, conn, keys, data_iter):
    from sqlalchemy.dialects.postgresql import insert

    data = [dict(zip(keys, row)) for row in data_iter]

    insert_statement = insert(table.table).values(data)
    upsert_statement = insert_statement.on_conflict_do_update(
        constraint=f"{table.table.name}_pkey",
        set_={c.key: c for c in insert_statement.excluded},
    )
    conn.execute(upsert_statement)


if __name__ == '__main__':
    logging.info('----Runing Script----')
    try:
        alchemyEngine = create_engine('postgresql+psycopg2://postgres:postgres@host.docker.internal/football', pool_pre_ping=True,
                                      pool_recycle=3600,
                                      connect_args={
                                          "keepalives": 1,
                                          "keepalives_idle": 30,
                                          "keepalives_interval": 10,
                                          "keepalives_count": 5,
                                      })

        # Connect to PostgreSQL server
        dbConnection = alchemyEngine.connect()

        try:
            competitions_result = pd.DataFrame.from_dict(
                get_football_data_api('competitions', 'competitions'))
            print(competitions_result)

            competitions = competitions_result[['id', 'name']]
            competitions.to_sql(name='dim_competitions',
                                con=dbConnection, if_exists='append', index=False, method=postgres_upsert)
        except Exception as e:
            logging.error(traceback.print_exc())
            logging.error('Error in saving data to postgress' + str(e))
            raise Exception(e)

        try:
            for index, row in competitions.iterrows():
                uri_end = 'competitions/' + str(row['id']) + '/teams'
                print('Calling football data api for ' + str(row['id']))
                teams = pd.DataFrame.from_dict(get_football_data_api(
                    uri_end, 'teams'))
                if not teams.empty:
                    team_df = teams[['id', 'name']]
                    team_df.to_sql(name='dim_teams', con=dbConnection,
                                   if_exists='append', index=False, method=postgres_upsert)

                    fact_competitions_df = team_df[['id']]
                    fact_competitions_df['team_id'] = fact_competitions_df['id']
                    fact_competitions_df.pop('id')
                    fact_competitions_df['competition_id'] = row['id']
                    fact_competitions_df.to_sql(
                        name='fact_competitions', con=dbConnection, if_exists='append', index=False, method=postgres_upsert)
                else:
                    print(str(row['id']) + ' has no teams associated')
                time.sleep(5)
        except Exception as e:
            logging.error(traceback.print_exc())
            logging.error('Error in saving data to postgress' + str(e))
            raise Exception(e)

        # Read data from PostgreSQL database table and load into a DataFrame instance
        dataFrame = pd.read_sql('SELECT * FROM dim_teams', dbConnection)
        dataFrame2 = pd.read_sql('SELECT * FROM fact_competitions', dbConnection)

        pd.set_option('display.expand_frame_repr', False)

        print(dataFrame)
        print(dataFrame2)
        dbConnection.close()
    except Exception as e:
        logging.error(traceback.print_exc())
        logging.error('Error in SQL' + str(e))
        raise Exception(e)
