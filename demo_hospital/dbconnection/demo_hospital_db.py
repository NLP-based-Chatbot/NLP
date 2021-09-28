import sqlalchemy
from sqlalchemy import create_engine,Column,Integer,String,Time,Date,ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os
import re

uri = os.getenv("DATABASE_URL")  # or other relevant config var
#if uri.startswith("postgres://"):
#    uri = uri.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`

if uri==None or uri=="":
    engine = create_engine("postgresql://wingmanuser:wingmanuser@localhost:5432/hospital_demo", echo=False)
    #engine = create_engine("postgresql://lezkthpysqsmok:59a647db86f9a0ef9909edfaa3d8396cf75274a2956a45fc127ae06864ebf637@ec2-44-198-151-32.compute-1.amazonaws.com:5432/dd5nbunbcg2ar8", echo=False)
    print("DB connection success")
else:
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
        engine = create_engine(uri)
        print("DB connection success")
        
        
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Doctor(Base):
    
    __tablename__ = "doctor"
    
    doctor_id   =   Column(Integer(),primary_key=True)
    initials    =   Column(String(10))
    first_name  =   Column(String(30))
    last_name   =   Column(String(30))
    docthash    =   Column(String(40))


class Appiontment(Base):

    __tablename__ = "appointments"

    appointment_id  = Column(String(30),primary_key=True)
    doctor_id       = Column(Integer(),ForeignKey("doctor.doctor_id"))
    cust_id         = Column(Integer(),ForeignKey("pstirnt.cust_id"))
    time_slot       = Column(Time())
    date            = Column(Date())

class DoctorAvailable(Base):

    __tablename__ = "doctor_availability"

    avbl_id     = Column(Integer(),primary_key=True)
    doctor_id   = Column(Integer(),ForeignKey("doctor.doctor_id"))
    date        = Column(Date())
    time_from   = Column(Time())
    time_to     = Column(Time())


class DoctorSpec(Base):

    __tablename__ = "doctor_specialization"

    d2s_id      = Column(Integer(),primary_key=True)
    doctor_id   = Column(Integer(),ForeignKey("doctor.doctor_id"))
    spec_id     = Column(Integer(),ForeignKey("specs.spec_id"))


class Specialization(Base):

    __tablename__ = "specs"

    spec_id     = Column(Integer(),primary_key=True)
    spec_name   = Column(String(30))

class Patient(Base):

    __tablename__ = "patient"

    cust_id     = Column(Integer,primary_key=True)
    username    = Column(String(100))
    userhash    = Column(String(40))

class Report(Base):

    __tablename__ = "reports"

    report_id   = Column(Integer,primary_key=True)
    cust_id     = Column(Integer,ForeignKey("patient.cust_id"))
    report_filename     = Column(String(100))
    reporthash  = Column(String(40))