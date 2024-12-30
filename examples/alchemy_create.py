from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData

engine = create_engine("sqlite:///db.sqlite3", echo=True)
metadata = MetaData()

test_table = Table("test_table", metadata, Column("id", Integer, primary_key=True),
                   Column("name", String(50)))

metadata.create_all(engine)  # Manually create tables
