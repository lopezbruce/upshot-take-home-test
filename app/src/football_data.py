import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import logging
import traceback
import json
import requests

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

        competitions_result = pd.DataFrame.from_dict(get_football_data_api('competitions','competitions'))
        print(competitions_result)

        competitions = competitions_result[['id','name']]
        competitions.to_sql(name='dim_competitions', con=dbConnection, if_exists = 'append', index = False)

        # Read data from PostgreSQL database table and load into a DataFrame instance
        dataFrame = pd.read_sql('SELECT * FROM dim_competitions', dbConnection)

        pd.set_option('display.expand_frame_repr', False)

        print(dataFrame)
        dbConnection.close()
    except Exception as e:
        logging.error(traceback.print_exc())
        logging.error('Error in SQL' + str(e))
        raise Exception(e)
