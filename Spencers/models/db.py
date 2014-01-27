#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()
from gluon.dal import MySQLAdapter
#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()
MySQLAdapter.driver = globals().get('MySQLdb',None)

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL("mysql://root:1234@localhost/phase5",pool_size=3,migrate=True)
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))



## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')


import uuid
user_id = auth.user.id if auth.user else 0
unique_id = Field('unique_id','boolean',default=uuid.uuid4(),writable=False,readable=False)
active = Field('active','boolean',default=True,writable=False)
created_by = Field('created_by',db.auth_user,default=user_id,writable=False)
created_on = Field('created_on','datetime',default=request.now,writable=False) 
modified_by = Field('modified_by',db.auth_user,default=user_id,update=user_id,writable=False)
modified_on = Field('modified_on','datetime',default=request.now,update=request.now,writable=False)
#########################################################################
## Define your tables below (or better in another model file) for example
##
db.define_table('DEALERS',
                Field('dealer_name','string',requires = IS_MATCH('[a-zA-Z ][^!@#$%^&*]',error_message='Not a valid Name')),
                Field('office_add','text'),
                Field('ship_add','text'),
                Field('mobile',requires = IS_MATCH('^\d{10}',error_message='NOT A VALID NAMEss')),
                Field('email',requires = IS_EMAIL(error_message='invalid email!')),
               
                format='%(dealer_name)s'
                )


db.define_table('PRODUCTS',
                Field('item_name','string',requires = IS_MATCH('[a-zA-Z ][^!@#$%^&*]',error_message='Not a valid Product Name')),
                Field('mrp','integer',notnull=True,requires = IS_MATCH('^\d',error_message='Not a valid Amount')),
                Field('discount','integer'),
                Field('dealer','reference DEALERS'),
                format='%(item_name)s')


db.define_table('CUSTOMERS',
                Field('cust_name','string',requires = IS_MATCH('[a-zA-Z ][^!@#$%^&*]',error_message='Not a valid Name')),
                Field('address','text'),
                Field('mobile',requires = IS_MATCH('^\d{10}',error_message='Not a valid Indian Mobile Number')),
                Field('email',requires = IS_EMAIL(error_message='invalid email!')),                
                format='%(cust_name)s')



db.define_table('FBACK',
                Field('name','string',requires = IS_MATCH('[a-zA-Z ][^!@#$%^&*]',error_message='Not a valid Name')),
                Field('email',requires=IS_EMAIL(error_message='invalid email!')),
                Field('Feedback','text'))

db.define_table('BILLS',
                Field('customer','reference CUSTOMERS'),
                Field('total','integer',default=0,readable=False,writable=False),
                Field('net_total','integer',readable=False,writable=False)
                )

db.define_table('BILLITEMS',
                Field('bill','reference BILLS',readable=False,writable=False),
                Field('product','reference PRODUCTS'),
                Field('quantity','integer'))
