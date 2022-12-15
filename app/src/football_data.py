import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import logging
import traceback

if __name__ == '__main__':
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

        # Read data from PostgreSQL database table and load into a DataFrame instance
        dataFrame = pd.read_sql('SELECT * FROM dim_teams', dbConnection)

        pd.set_option('display.expand_frame_repr', False)

        print(dataFrame)
        dbConnection.close()
    except Exception as e:
        logging.error(traceback.print_exc())
        logging.error('Error in SQL' + str(e))
        raise Exception(e)
