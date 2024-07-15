from pandas import DataFrame
from openai_functools import openai_function


from database import session, engine

from sqlalchemy import text
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.schema import CreateTable


@openai_function
def get_db_schema() -> str:
    '''Returns the DB schema as a SQL create statement with string format'''
    #engine = create_engine('sqlite:///ecommerce.db')
    try:
        Base = automap_base()
        Base.prepare(engine, reflect=True)
        tables = Base.classes.keys()
        schema = ""

        for table in tables:
            table_obj = Base.classes[table].__table__
            schema += str(CreateTable(table_obj)) + ";\n"

        return schema
    
    except Exception as e:
        raise e

@openai_function
def query_db(query:str) -> dict:
    '''
    Executes a query on the SQL database and returns the result as a dictionary.
    :param query: A valid SQL query that will be executed on the database.
    :return: A dictionary containing the result of the query
    '''
    dict_result = {}
    try:
        result = session.execute(text(query))
        # Convert the result to a dictionary
        dict_result = DataFrame(result.fetchall(), columns=result.keys()).to_dict()
        return dict_result
    
    except Exception as e:
        raise e
