from sqlalchemy import func
from drivers_backend.db import db


class DriverModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    firstname = db.Column(db.String(250))
    lastname = db.Column(db.String(250))
    usernamemain = db.Column(db.String(250))
    residentialaddress = db.Column(db.String(250))
    email = db.Column(db.String(250), unique=True)
    phoneno = db.Column(db.String(250))
    status = db.Column(db.String(250), default='0')
    pin = db.Column(db.String(250))
    operatorid = db.Column(db.String(250))
    bankname = db.Column(db.String(250))
    accountname = db.Column(db.String(250))
    accountnumber = db.Column(db.String(250))
    license = db.Column(db.String(250))
    zone = db.Column(db.String(250))
    area = db.Column(db.String(250))
    route = db.Column(db.String(250))
    geofencedarea = db.Column(db.String(250))
    appstatus = db.Column(db.String(250), default='0')
    acceptstatus = db.Column(db.String(250), default='0')
    approvedtimestamp = db.Column(db.DateTime)
    accepttimestamp = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, server_default=func.now())
