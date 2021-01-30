# Upsert operations to load test_csv data into the system.

from emis_app import db, bcrypt
from sqlalchemy.dialects.postgresql import insert
from emis_app.csv_ops import read_csv_data

def emis_users_dict_pair(tuple_):
    hashed_password = bcrypt.generate_password_hash(
        tuple_[5]).decode('utf-8')
    return dict(id=tuple_[0]), dict(
        username=tuple_[1],
        fullname=tuple_[2],
        position=tuple_[3],
        email=tuple_[4],
        password=hashed_password,
        site_id=tuple_[6],
        auth_level=tuple_[7]
    )

def mst_change_log_dict_pair(tuple_):
    return dict(id=tuple_[0]), dict(
        maint_log_id=tuple_[1],
        maint_status_from=tuple_[2],
        maint_status_to=tuple_[3],
        change_date=tuple_[4]
    )

def maint_status_dict_pair(tuple_):
    return dict(id=tuple_[0]), dict(
        description=tuple_[1]
    )    

def maint_types_dict_pair(tuple_):
    return dict(id=tuple_[0]), dict(
        description=tuple_[1]
    )

def maint_sites_dict_pair(tuple_):
    return dict(id=tuple_[0]), dict(
        name=tuple_[1],
        grade=tuple_[2],
        contact_id=tuple_[3],
        last_audit=tuple_[4]
    )

def engines_dict_pair(tuple_):
    return dict(eng_sn=tuple_[0]), dict(
        eng_pn=tuple_[1],
        customer=tuple_[2],
        maint_site_id=tuple_[3],
        build_date=tuple_[4],
        op_hrs=tuple_[5],
        cycle=tuple_[6],
        status_id=tuple_[7]
        ) 

def engines_status_dict_pair(tuple_):
    return dict(id = tuple_[0]), dict(description = tuple_[1])

def maint_log_dict_pair(tuple_):
    return dict(id=tuple_[0]), dict(
        eng_sn=tuple_[1],
        maint_site_id=tuple_[2],
        maint_type_id=tuple_[3],
        maint_status_id=tuple_[4],
        owner_id=tuple_[5],
        in_date=tuple_[6],
        out_date=tuple_[7],
        maint_cost=tuple_[8],
        note=tuple_[9]
    )
# Helper function for upsert_from_csv(). Note that the dict_pair should be a function.
def insert_tuples(table_obj, dict_pair, tuples, sql_engine):
    for tuple_ in tuples:
        dict_head, dict_remain = dict_pair(tuple_)
        insert_stmt = insert(table_obj).values(**dict_head, **dict_remain)\
            .on_conflict_do_update(constraint=table_obj.primary_key,
            set_=dict_remain)
        sql_engine.connect().execute(insert_stmt)    

def upsert_from_csv(data_model, filename):
    sql_engine = db.get_engine()
    table = data_model.__table__
    tuples = read_csv_data(filename)
    if data_model.__tablename__ == 'engines':
        insert_tuples(table, engines_dict_pair, tuples, sql_engine)
    elif data_model.__tablename__ == 'engine_status':
        insert_tuples(table, engines_status_dict_pair, tuples, sql_engine)
    elif data_model.__tablename__ == 'maint_sites':
        insert_tuples(table, maint_sites_dict_pair, tuples, sql_engine)
    elif data_model.__tablename__ == 'maint_types':
        insert_tuples(table, maint_types_dict_pair, tuples, sql_engine)
    elif data_model.__tablename__ == 'maint_log':
        insert_tuples(table, maint_log_dict_pair, tuples, sql_engine)
    elif data_model.__tablename__ == 'maint_status':
        insert_tuples(table, maint_status_dict_pair, tuples, sql_engine)
    elif data_model.__tablename__ == 'mst_change_log':
        insert_tuples(table, mst_change_log_dict_pair, tuples, sql_engine)
    elif data_model.__tablename__ == 'emis_users':
        insert_tuples(table, emis_users_dict_pair, tuples, sql_engine)
    else:
        raise Exception('data_model not available for upsert operations.')