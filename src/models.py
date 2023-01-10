from sqlalchemy import Column, DateTime, Integer, String, func, Float, BigInteger, Boolean, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.expression import case
from typing import List, AnyStr
from datetime import datetime
from .connect import engine, session
from .config import ProdConfig
from re import search
from json import loads

Base = declarative_base()


class ValidatorLog(Base):
    __tablename__ = "validatorlog"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    filename = Column(String(500), nullable=False)
    log_entry = Column(String(2000), nullable=False)
    log_context = Column(String(100), nullable=True)
    log_type = Column(String(50), nullable=True)
    _json = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    #TODO: Debig. Almost none of the matches are stored in the DB.
    def load_list_matches(filename: AnyStr, matches_list: List) -> None:
        try:
            for val in matches_list:
                stripped_entry = val[28::]
                match_obj = search("\[(.*?)\]", stripped_entry)
                context = match_obj[0] if match_obj else None
                match_obj = search("(\s[A-Z]+\s)", stripped_entry)
                ltype = match_obj[0].strip() if match_obj else None
                try:
                    match_obj = search(r"\s([{\[].*?[}\]])$", stripped_entry)
                    j_son = match_obj[0] if match_obj else None
                except Exception as bla:
                    j_son = None
                vlog = ValidatorLog(
                    timestamp = datetime.strptime(val[0:19:], '%Y-%m-%dT%H:%M:%S'),
                    filename = filename,
                    log_entry = stripped_entry,
                    log_context = context,
                    log_type = ltype,
                    _json = j_son,
                )
                session.add(vlog)
            session.commit()
        except Exception as e:
            # TODO add proper logging + throw specific exception to break when called in a loop
            print(f"[{datetime.now()}]:{e}")

# Create the model if it doesn't exist already
Base.metadata.create_all(engine)

# Truncate the tables if needed
if ProdConfig.INITIATE_MODEL == 1:
    try:
        num_rows_deleted = session.query(ValidatorLog).delete()
        print(f"{num_rows_deleted} rows deleted!")
        session.commit()
    except:
        session.rollback()
