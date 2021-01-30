""" Database models for the system """
from emis_app import db, login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Emis_users.query.get(int(user_id))

class Emis_users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    fullname = db.Column(db.String(40), unique=True, nullable=False)
    position = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    site_id = db.Column(db.String(10),nullable=False)

    # 1: overall, 2: site manager, 3: site engineer
    auth_level = db.Column(db.Integer, nullable=False) 
    
    maint_sites = db.relationship('Maint_sites', back_populates='emis_users')
    maint_log = db.relationship('Maint_log', back_populates='emis_users')

class User_messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('emis_users.id'), 
                        nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('emis_users.id'), 
                                nullable=False)
    sent_time = db.Column(db.DateTime, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False)
    message = db.Column(db.String, nullable=False)

    emis_users = db.relationship('Emis_users', foreign_keys=[user_id])
    emis_users_2 = db.relationship('Emis_users', foreign_keys=[from_user_id])

class Mst_change_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maint_log_id = db.Column(db.Integer, db.ForeignKey('maint_log.id'),
        nullable=False)
    maint_status_from = db.Column(db.Integer, db.ForeignKey('maint_status.id'),
        nullable=False)
    maint_status_to   = db.Column(db.Integer, db.ForeignKey('maint_status.id'),
        nullable=False)
    change_date = db.Column(db.Date, nullable=False)

    maint_log = db.relationship('Maint_log', back_populates='mst_change_log')
    maint_status = db.relationship('Maint_status', 
                                    foreign_keys=[maint_status_from])
    maint_status2 = db.relationship('Maint_status', 
                                    foreign_keys=[maint_status_to])

class Maint_status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), nullable=False)
    maint_log = db.relationship('Maint_log', back_populates='maint_status')


class Maint_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), nullable=False)

    maint_log = db.relationship('Maint_log', back_populates='maint_types')

class Maint_sites(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('emis_users.id'))
    last_audit = db.Column(db.Date, nullable=False)
    
    engines = db.relationship('Engines', back_populates='maint_sites')
    maint_log = db.relationship('Maint_log', back_populates='maint_sites')
    emis_users = db.relationship('Emis_users', back_populates='maint_sites')

class Engine_status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), nullable=False)

    engines = db.relationship('Engines', back_populates='engine_status')

class Engines(db.Model):
    eng_sn = db.Column(db.String(20), primary_key=True)
    eng_pn = db.Column(db.String(20), nullable=False)
    customer = db.Column(db.String(10),nullable=False)
    maint_site_id = db.Column(db.String(10), db.ForeignKey('maint_sites.id'),
        nullable=False)
    build_date = db.Column(db.Date, nullable=False)
    op_hrs = db.Column(db.Numeric, nullable=False)
    cycle = db.Column(db.Numeric, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('engine_status.id'),
        nullable=False)
    
    engine_status = db.relationship('Engine_status', back_populates='engines')
    maint_sites = db.relationship('Maint_sites', back_populates='engines')
    maint_log = db.relationship('Maint_log', back_populates='engines')

class Maint_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eng_sn = db.Column(db.String(20), db.ForeignKey('engines.eng_sn'),
        nullable=False)
    maint_site_id = db.Column(db.String(10), db.ForeignKey('maint_sites.id'),
        nullable=False)
    maint_type_id = db.Column(db.Integer, db.ForeignKey('maint_types.id'),
        nullable=False)
    maint_status_id = db.Column(db.Integer, db.ForeignKey('maint_status.id'),
        nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('emis_users.id'))
    in_date = db.Column(db.Date, nullable=False)
    out_date = db.Column(db.Date)
    maint_cost = db.Column(db.Numeric)
    note = db.Column(db.String(200))
    
    maint_types = db.relationship('Maint_types', back_populates='maint_log')
    engines = db.relationship('Engines', back_populates='maint_log')
    maint_sites = db.relationship('Maint_sites', back_populates='maint_log')
    maint_status = db.relationship('Maint_status', back_populates='maint_log')
    mst_change_log = db.relationship('Mst_change_log', 
                                      back_populates='maint_log')
    emis_users = db.relationship('Emis_users')