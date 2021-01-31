from flask import render_template, jsonify, request, redirect, url_for, flash
from emis_app.form import LoginForm, AddUserForm
from emis_app import app, db, bcrypt
from emis_app.models import (
    Engines, Engine_status, Maint_sites, 
    Maint_types, Maint_status, Maint_log,
    Mst_change_log, Emis_users
    )
from emis_app.upsert_ops import upsert_from_csv
from sqlalchemy import or_, desc, func, distinct
from flask_login import login_user, current_user, logout_user, login_required
from pathlib import Path

@app.context_processor
def inject_user():
    return dict(base_user=Emis_users)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/thumbnail')
def thumbnail():
    return render_template('thumbnail.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/users")
@login_required
def users():
    result = Emis_users.query.filter(Emis_users.id != 1).all()
    return render_template('users.html', emis_users = result)

@app.route('/user_setting', methods=['GET', 'POST'])
def user_setting():
    add_user_form = AddUserForm()
    if request.method == 'POST':
        if add_user_form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(
                add_user_form.password.data).decode('utf-8')
            user = Emis_users(
                username=add_user_form.username.data, 
                fullname=add_user_form.fullname.data,
                email=add_user_form.email.data, 
                password=hashed_password
                )
            db.session.add(user)
            db.session.commit()
            flash('User added sucessfully.', 'success')
        else:
            flash('Failed adding users.', 'danger')

    return render_template('user_setting.html', add_user_form=add_user_form)


@app.route('/login', methods=['GET','POST'])
def login():
    login_form = LoginForm()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            user = Emis_users.query.filter(
                Emis_users.username == login_form.username.data).first()
            if  user and bcrypt.check_password_hash(user.password, 
                                                    login_form.password.data):
                login_user(user) # rememeber set as false
                return redirect(url_for('dashboard'))
        
        flash('Login failed.', 'danger')
    return render_template('login.html',login_form = login_form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html', user = Emis_users)


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.auth_level == 1:
        get_avg_turnaround_time()
        return render_template('dashboard1.html') # for authorization level 1
    else:
        return render_template('dashboard2.html') # for authorization level 2

@app.route('/get_dashboard_info')
@login_required
def get_dashboard_info():
    if current_user.auth_level == 1:
        dashboard_info_dict = dashboard_info_auth_1()
    else:
        dashboard_info_dict = dashboard_info_auth_2()
    return jsonify(dashboard_info_dict)




@app.route('/engine_list')
@app.route('/engine_list/<options>')
@login_required
def engine_list(options='111'):
    if current_user.auth_level == 1:
        if options == '111' or options == 'search_result':
            engine_objects = Engines.query.order_by(Engines.eng_sn).all()
        elif options == '011':
            engine_objects = Engines.query.filter(Engines.status_id != 1).\
                order_by(Engines.eng_sn).all()
        elif options == '101':
            engine_objects = Engines.query.filter(Engines.status_id != 2).\
                order_by(Engines.eng_sn).all()
        elif options == '110':
            engine_objects = Engines.query.filter(
                Engines.status_id != 3, Engines.status_id != 4).\
                    order_by(Engines.eng_sn).all()
        elif options == '001':
            engine_objects = Engines.query.filter(
                or_(Engines.status_id == 3, Engines.status_id == 4)).\
                    order_by(Engines.eng_sn).all()
        elif options == '010':
            engine_objects = Engines.query.filter(Engines.status_id == 2).\
                order_by(Engines.eng_sn).all()
        elif options == '100':
            engine_objects = Engines.query.filter(Engines.status_id == 1).\
                order_by(Engines.eng_sn).all()
        elif options == '000':
            engine_objects = []
        else: 
            # user try to input the options manually and it's non-existant.
            options = 111
            engine_objects = Engines.query.order_by(Engines.eng_sn).all()
    else: # secondary authorization level:
        site_id = current_user.site_id
        if options == '111' or options == 'search_result':
            engine_objects = Engines.query.filter(
                Engines.maint_site_id == site_id).\
                order_by(Engines.eng_sn).all()
        elif options == '011':
            engine_objects = Engines.query.filter(Engines.status_id != 1).\
                filter(Engines.maint_site_id == site_id).\
                    order_by(Engines.eng_sn).all()
        elif options == '101':
            engine_objects = Engines.query.filter(Engines.status_id != 2).\
                filter(Engines.maint_site_id == site_id).\
                    order_by(Engines.eng_sn).all()
        elif options == '110':
            engine_objects = Engines.query.filter(
                Engines.status_id != 3, Engines.status_id != 4).\
                    filter(Engines.maint_site_id == site_id).\
                        order_by(Engines.eng_sn).all()
        elif options == '001':
            engine_objects = Engines.query.filter(
                or_(Engines.status_id == 3, Engines.status_id == 4)).\
                    filter(Engines.maint_site_id == site_id).\
                        order_by(Engines.eng_sn).all()
        elif options == '010':
            engine_objects = Engines.query.filter(Engines.status_id == 2).\
                filter(Engines.maint_site_id == site_id).\
                    order_by(Engines.eng_sn).all()
        elif options == '100':
            engine_objects = Engines.query.filter(Engines.status_id == 1).\
                filter(Engines.maint_site_id == site_id).\
                    order_by(Engines.eng_sn).all()
        elif options == '000':
            engine_objects = []
        else:
            options = 111
            engine_objects = Engines.query.order_by(Engines.eng_sn).\
                filter(Engines.maint_site_id == site_id).all()
    return render_template('engine_list.html', 
                            options=options, engine_objects=engine_objects)


@app.route('/get_engine_info/<eng_sn>')
@login_required
def get_engine_info(eng_sn):
    if request.method == 'GET':
        if len(db.session.query(Maint_log).\
                filter(Maint_log.eng_sn == eng_sn).all()) != 0:
            engine_info = db.session.query(
                Engines, Maint_sites, Engine_status, Maint_log, Maint_status).\
                filter(Engines.eng_sn == eng_sn).\
                filter(Maint_sites.id == Engines.maint_site_id).\
                filter(Engine_status.id == Engines.status_id).\
                filter(Maint_log.eng_sn == eng_sn).\
                filter(Maint_status.id == Maint_log.maint_status_id).\
                order_by(desc(Maint_log.in_date)).first()
            has_maint_log = True
        else:
            engine_info = db.session.query(Engines, Maint_sites, Engine_status).\
                filter(Engines.eng_sn == eng_sn).\
                filter(Maint_sites.id == Engines.maint_site_id).\
                filter(Engine_status.id == Engines.status_id).first()
            has_maint_log = False

        engine_info_dict = {
            'eng_sn' : engine_info[0].eng_sn,
            'eng_pn' : engine_info[0].eng_pn,
            'customer' : engine_info[0].customer,
            'maint_site' : engine_info[1].name,
            'build_date' : engine_info[0].build_date.strftime("%d %b %Y"),
            'op_hrs' : str(engine_info[0].op_hrs),
            'cycle' : str(engine_info[0].cycle),
            'engine_status' : engine_info[2].description,
            'maint_log_id' : 'N/A',
            'maint_status' : 'No Record'
        }
        if has_maint_log :
            append_dict = {
                'maint_log_id' : engine_info[3].id,
                'maint_status' : engine_info[4].description
            }
            engine_info_dict.update(append_dict)
        return engine_info_dict

@app.route('/maint_log_list')
@login_required
def maint_log_list():
    return render_template('maint_log_list.html')

@app.route('/get_main_log_list_info/<is_active_only>')
@login_required
def get_maint_log_list_info(is_active_only):
    if is_active_only == '1':
        maint_log_stmt = db.session.query(
            Maint_log, Maint_types, Maint_status, Emis_users).\
            filter(Maint_log.maint_status_id != 13).\
            filter(Maint_log.maint_type_id == Maint_types.id).\
            filter(Maint_log.maint_status_id == Maint_status.id).\
            filter(Maint_log.owner_id == Emis_users.id)
        if current_user.auth_level == 2:
            maint_log_stmt = maint_log_stmt.filter(
                Maint_log.maint_site_id == current_user.site_id)
        maint_log_objects = maint_log_stmt.all()
    else:
        maint_log_stmt = db.session.query(
            Maint_log, Maint_types, Maint_status, Emis_users).\
            filter(Maint_log.maint_type_id == Maint_types.id).\
            filter(Maint_log.maint_status_id == Maint_status.id).\
            filter(Maint_log.owner_id == Emis_users.id)
        if current_user.auth_level == 2:
            maint_log_stmt = maint_log_stmt.filter(
                Maint_log.maint_site_id == current_user.site_id)
        maint_log_objects = maint_log_stmt.all()
    

    maint_log_dict_list = []
    for tuple_ in maint_log_objects:
        if tuple_[0].out_date == None:
            out_date = 'N/A'
        else:
            out_date = tuple_[0].out_date.strftime("%d %b %Y")
        
        if tuple_[0].note == None:
            note = ''
        else:
            note = tuple_[0].note

        dict_ = {
            'maint_log_id' : str(tuple_[0].id),
            'eng_sn' : tuple_[0].eng_sn,
            'maint_site_id': tuple_[0].maint_site_id,
            'maint_type': tuple_[1].description,
            'maint_status': tuple_[2].description,
            'owner_id' : str(tuple_[0].owner_id),
            'owner_name' : tuple_[3].fullname,
            'owner_email' : tuple_[3].email,
            'in_date' : tuple_[0].in_date.strftime("%d %b %Y"),
            'out_date' : out_date,
            'maint_cost' : str(tuple_[0].maint_cost),
            'note' : note
        }
        maint_log_dict_list.append(dict_)
    return jsonify(maint_log_dict_list)

@app.route('/site_list')
@login_required
def site_list():
    if current_user.auth_level == 1:
        site_objects = db.session.query(Maint_sites).all()
        return render_template('site_list.html', site_objects=site_objects)
    else:
        return redirect(url_for('site_list_search', 
                        search_str=f"search_result_{current_user.site_id}"))

@app.route('/site_list/<search_str>')
@login_required
def site_list_search(search_str):
    target = search_str.replace("search_result_","")
    site_objects = db.session.query(Maint_sites).\
        filter(Maint_sites.id == target).all()
    return render_template('site_list.html', site_objects=site_objects)

@app.route('/get_site_engine_info/<site_id>')
def get_site_engine_info(site_id):
    site_engine_info = db.session.query(Engines, Maint_log, Maint_status).\
        filter(or_(Engines.status_id == 2, Engines.status_id == 4)).\
        filter(Engines.maint_site_id == site_id)
    
    dict_list = []
    if len(site_engine_info.all()) != 0:
        tuple_list = site_engine_info.filter(Maint_log.eng_sn == Engines.eng_sn).\
            filter(Maint_log.maint_status_id == Maint_status.id).all()
        for tuple_ in tuple_list:
            site_engine_info_dict = {
                'eng_sn' : tuple_[0].eng_sn,
                'eng_pn' : tuple_[0].eng_pn,
                'in_date' : tuple_[1].in_date.strftime("%d %b %Y"),
                'maint_status' : tuple_[2].description,
                'maint_site_id' : tuple_[0].maint_site_id
            }
            dict_list.append(site_engine_info_dict)
    return jsonify(dict_list)



@app.route('/search')
@login_required
def search():
    target_str = request.args.get('q')
    # site id rule: 
    #   3-4 letters, first three must be uppercase letters
    # engine sn rule: 
    #   first letter will be uppercase letters, length will exeeds 5
    # maint_log_id : 
    #   pure numbers
    if len(target_str) == 0:
        return redirect(url_for('dashboard'))
    
    # Engine Search
    elif target_str[0].isupper() and len(target_str) >= 5:
        query_stmt = db.session.query(Engines).\
            filter(Engines.eng_sn == target_str)
        if current_user.auth_level == 2:
            query_stmt = query_stmt.filter(
                Engines.maint_site_id == current_user.site_id)
        
        sn_exist = db.session.query(query_stmt.exists()).scalar() 
        
        if sn_exist:
            return redirect(
                url_for('engine_list', options=f"search_result_{target_str}"))
        else:
            return render_template('search_no_match.html',target_str=target_str)
    
    # Site Search
    elif target_str[0:3].isalpha() and target_str[0:3].isupper():
        query_stmt = db.session.query(Maint_sites).\
            filter(Maint_sites.id == target_str)
        if current_user.auth_level == 2:
            query_stmt = query_stmt.filter(
                Maint_sites.id == current_user.site_id)
        
        sn_exist = db.session.query(query_stmt.exists()).scalar()
        
        if sn_exist:
            return redirect(
                url_for('site_list_search', search_str=f"search_result_{target_str}"))
        else:
            return render_template('search_no_match.html',target_str=target_str)
    
    # Maint Log Search
    elif target_str.isdigit(): 
        log_stmt = db.session.query(
            Maint_log, Maint_types, Maint_status, Emis_users).\
            filter(Maint_log.id == int(target_str)).\
            filter(Maint_log.maint_type_id == Maint_types.id).\
            filter(Maint_log.maint_status_id == Maint_status.id).\
            filter(Maint_log.owner_id == Emis_users.id)
        if current_user.auth_level == 2:
            log_stmt = log_stmt.filter(
                Maint_log.maint_site_id == current_user.site_id)
        log = log_stmt.all()
        if len(log) != 0:
            return render_template('maint_log_search_result.html', log=log[0])

    return render_template('search_no_match.html', target_str=target_str)

# For pour in dummy data only. These are PostgreSQL upsert operations so
# updating the csv files will not have any issue as long as the data format is 
# correct.

# @app.route('/upsert_action_page')
# def upsert_action_page():
#     db.create_all()
#     path = Path(__file__).parent
#     upsert_from_csv(Maint_status, f'{path}/emis_demo_data/maint_status.csv')
#     upsert_from_csv(Maint_types, f'{path}/emis_demo_data/maint_types.csv')
#     upsert_from_csv(Engine_status, f'{path}/emis_demo_data/engine_status.csv')
#     upsert_from_csv(Emis_users, f'{path}/emis_demo_data/emis_users.csv')
#     upsert_from_csv(Maint_sites, f'{path}/emis_demo_data/maint_sites.csv')
#     upsert_from_csv(Engines, f'{path}/emis_demo_data/engines.csv')
#     upsert_from_csv(Maint_log, f'{path}/emis_demo_data/maint_log.csv')
#     upsert_from_csv(Mst_change_log, f'{path}/emis_demo_data/mst_change_log.csv')
#     return render_template('upsert_complete.html', 
#                             Engines=Engines, session=db.session) 

# dashboard helper functions

def dashboard_info_auth_1():
    engine_count = db.session.query(func.count(Engines.eng_sn)).first()[0]
    type_count = db.session.query(func.count(distinct(Engines.eng_pn))).first()[0]
    site_count = db.session.query(func.count(Maint_sites.id)).first()[0]
    customer_count = db.session.query(func.count(distinct(Engines.customer))).first()[0]
    service_count = db.session.query(Engines).filter(Engines.status_id == 1).count()
    repairing_count = db.session.query(Engines).filter(Engines.status_id == 2).count()
    transit_count = db.session.query(Engines).filter(Engines.status_id == 3).count()
    RD_count = db.session.query(Engines).filter(Engines.status_id == 4).count()
    turnaround_time_list = get_avg_turnaround_time()

    pending_engine_object = db.session.query(Engines, Maint_log, Maint_status, Emis_users).\
        filter(Engines.eng_sn == Maint_log.eng_sn).\
        filter(Maint_log.maint_status_id == Maint_status.id).\
        filter(Maint_log.owner_id == Emis_users.id).\
        filter(or_(Maint_log.maint_status_id == 3, 
                   Maint_log.maint_status_id == 5,
                   Maint_log.maint_status_id == 7,
                   Maint_log.maint_status_id == 11)).all()
    pending_dict_list = []
    for tuple_ in pending_engine_object:
        dict_ = {
            'eng_sn' : tuple_[0].eng_sn,
            'site_id' : tuple_[1].maint_site_id,
            'maint_log_id' : tuple_[1].id,
            'maint_status' : tuple_[2].description,
            'in_date': tuple_[1].in_date.strftime("%d %b %Y"),
            'owner_id' : tuple_[3].id,
            'owner_name': tuple_[3].fullname
        }
        pending_dict_list.append(dict_)
    
    dashboard_info_dict = {
        'auth_level' : current_user.auth_level,
        'engine_count' : engine_count,
        'type_count' : type_count,
        'site_count' : site_count,
        'customer_count' : customer_count,
        'service_count' : service_count,
        'repairing_count' : repairing_count,
        'transit_count' : transit_count,
        'RD_count' : RD_count,
        'pending_engines' : pending_dict_list,
        'TAT_list' : turnaround_time_list
    }

    return dashboard_info_dict

def dashboard_info_auth_2():
    site_id = current_user.site_id
    engine_count = len(Engines.query.filter(
                            Engines.maint_site_id == site_id).all())
    on_site_count = len(Engines.query.\
                            filter(Engines.maint_site_id == site_id).\
                            filter(or_(Engines.status_id == 2, 
                                        Engines.status_id == 4)).all())
    transit_count = len(Engines.query.\
                            filter(Engines.maint_site_id == site_id).\
                            filter(Engines.status_id == 3).all())
    pending_engine_object = db.session.query(
        Engines, Maint_log, Maint_status, Emis_users).\
        filter(Engines.eng_sn == Maint_log.eng_sn).\
        filter(Maint_log.maint_status_id == Maint_status.id).\
        filter(Maint_log.owner_id == Emis_users.id).\
        filter(or_(Maint_log.maint_status_id == 3, 
                   Maint_log.maint_status_id == 5,
                   Maint_log.maint_status_id == 7,
                   Maint_log.maint_status_id == 11)).\
        filter(Maint_log.maint_site_id == site_id).all()
    pending_dict_list = []
    for tuple_ in pending_engine_object:
        dict_ = {
            'eng_sn' : tuple_[0].eng_sn,
            'maint_log_id' : tuple_[1].id,
            'maint_status' : tuple_[2].description,
            'in_date': tuple_[1].in_date.strftime("%d %b %Y"),
            'owner_id' : tuple_[3].id,
            'owner_name': tuple_[3].fullname
        }
        pending_dict_list.append(dict_)
    print(site_id)
    dashboard_info_dict = {
        'auth_level' : current_user.auth_level,
        'site_id' : site_id,
        'engine_count' : engine_count,
        'on_site_count' : on_site_count,
        'transit_count' : transit_count,
        'pending_engines' : pending_dict_list
    }

    return dashboard_info_dict

def get_avg_turnaround_time():
    db.session.query(Maint_log, Maint_sites).\
        filter(Maint_log.maint_status_id == 13)
    result = db.session.query(
        func.avg(Maint_log.out_date - Maint_log.in_date), 
                 Maint_log.maint_site_id).\
            filter(Maint_log.maint_status_id == 13).\
                group_by(Maint_log.maint_site_id).all()
    result_dict_list = []
    for tuple_ in result:
        dict_ = {
            'site_id' : tuple_[1],
            'TAT' :  f"{float(tuple_[0]):.2f}"
        }
        result_dict_list.append(dict_)
    return result_dict_list