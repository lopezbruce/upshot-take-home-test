import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import logging
import traceback
import datetime
import os

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'host.docker.internal')
DB_NAME = os.getenv('DB_NAME')
CONN_STRING = 'postgresql+psycopg2://'+DB_USERNAME + \
    ':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME

if __name__ == '__main__':
    utc_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    try:
        alchemyEngine = create_engine(CONN_STRING, pool_pre_ping=True,
                                      pool_recycle=3600,
                                      connect_args={
                                          "keepalives": 1,
                                          "keepalives_idle": 30,
                                          "keepalives_interval": 10,
                                          "keepalives_count": 5,
                                      })

        # Connect to PostgreSQL server
        dbConnection = alchemyEngine.connect()

        # Read data from PostgreSQL database table and load into a DataFrame instance
        dataFrame = pd.read_sql('SELECT t2.name AS "Competition", t1.number_of_teams AS "Number of Teams" FROM (SELECT competition_id, count(*) AS number_of_teams FROM fact_competitions GROUP BY 1) t1 INNER JOIN dim_competitions t2 ON t1.competition_id = t2.id ORDER BY t1.number_of_teams DESC', dbConnection)

        pd.set_option('display.expand_frame_repr', False)
        dataFrame.to_csv(
            '/output/output/data_from_football_data_org_'+utc_datetime+'.csv', index=False)
        print('\noutput summary: \n{}'.format(dataFrame))
        dbConnection.close()
    except Exception as e:
        logging.error(traceback.print_exc())
        logging.error('Error in creating the report' + str(e))
        raise Exception(e)
