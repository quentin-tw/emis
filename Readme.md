# EMIS

Website Link:
https://emisdemo.herokuapp.com

About Page:
https://emisdemo.herokuapp.com/about

Engine Management Information System (EMIS) is a Python Flask/javascript/PostgreSQL 
project to demonstrate basic functionalities of a website that can be used in 
aicraft engine maintenance factories. See about page for more information 
for general users.

## Using the source code

You can use the source code in your local machine. After cloning the repository,
build up the python virtual environment (`venv`) directory per `requirement.txt` . 
You will need to make an `.env` file inside the emis_app directory with your 
local database connection and secret key. You might start with `emis_app/example.env`.

Before running the app, you might want to have something to show in your database. 
The toy data are provided in the `emis_app/emis_demo_data` folder. if you are
using PostgreSQL database, then you can simply uncomment the `upsert_action_page()`
function in the `emis_app/route.py` file, and link to your localhost port with the page, for example: http://localhost:5000/upsert_action_page .

For other database you might need to modify the `emis_app/upsert_ops.py`, since it uses the [PostgreSQL dialect](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html) for upsert operations. See SQLAlchemy documentation for more details.

After setting up `venv` and `.env`, you can execute the linux shell script `run`:
```
./run
``` 



