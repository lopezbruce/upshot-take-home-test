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
        dataFrame = pd.read_sql('SELECT t2.name AS "Competition", t1.number_of_teams AS "Number of Teams" FROM (SELECT competition_id, count(*) AS number_of_teams FROM fact_competitions GROUP BY 1) t1 INNER JOIN dim_competitions t2 ON t1.competition_id = t2.id ORDER BY t1.number_of_teams DESC', dbConnection)

        pd.set_option('display.expand_frame_repr', False)
        dataFrame.to_csv(
            '/output/output/data_from_football_data_org.csv', index=False)
        print('\noutput summary: \n{}'.format(dataFrame))
        dbConnection.close()
    except Exception as e:
        logging.error(traceback.print_exc())
        logging.error('Error in creating the report' + str(e))
        raise Exception(e)
