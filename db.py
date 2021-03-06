from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine
import os


db = create_engine(os.environ['DATABASE_URL'])
metadata = MetaData(db)
'''
image_table = Table('images', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('user', Integer),
                    Column('filename', String)
                    )
'''
text_table = Table('text', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('user', Integer),
                   Column('text', String(240000))
                   )


def connect():
    with db.connect() as conn:
        text_table.create()

try:
    connect()
except:
    pass
