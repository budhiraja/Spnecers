# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


import os
import uuid
import subprocess
from appy.pod.renderer import Renderer

def createReport():
    persons = []
    for person in db().select(db.CUSTOMERS.ALL):
		persons.append(dict(cust_name=person.cust_name,email=person.mobile,address=person.email))
    # Report creation
    template_file = os.path.join(request.folder, 'template.odt')
    tmp_uuid = uuid.uuid4()
    output_file_odt = "/home/brat/%s.odt"%tmp_uuid    
    beingPaidForIt = True
    renderer = Renderer(template_file, locals(), output_file_odt)
    renderer.run()
    """subprocess.Popen("libreoffice --headless --invisible --convert-to pdf %s --outdir %s "%(output_file_odt, "/var/tmp") ,shell=True)
    while True:
    if os.path.exists(output_file_pdf):
    break
    data = open(output_file_pdf, "rb").read()
    for file in [output_file_odt, output_file_pdf]:
    os.unlink(file)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=PersonsListing.pdf'"""
    return data 




def user_manual():
    return locals()


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    if auth.is_logged_in():
        redirect(URL('onepage'))
    redirect(URL('user'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

@auth.requires_login() 
def onepage():
    dealers=db(db.DEALERS).select(orderby=db.DEALERS.dealer_name)
    products=db(db.PRODUCTS).select(orderby=db.PRODUCTS.item_name)
    customers=db(db.CUSTOMERS).select(orderby=db.CUSTOMERS.cust_name)
    return locals()
@auth.requires_membership('admin')
def edit_dealer():
    dealer = db.DEALERS(request.args(0)) or redirect(URL('view_dealers'))
    form = crud.update(db.DEALERS,dealer,next=URL('view_dealers'))
    return locals()
@auth.requires_membership('admin')
def edit_product():
    product = db.PRODUCTS(request.args(0)) or redirect(URL('view_products'))
    form = crud.update(db.PRODUCTS,product,next=URL('view_products'))
    return locals()
@auth.requires_membership('admin')
def edit_customer():
    customer = db.CUSTOMERS(request.args(0)) or redirect(URL('view_customers'))
    form = crud.update(db.CUSTOMERS,customer,next=URL('view_customers'))
    return locals()


@auth.requires_login() 
def customers():
    if auth.has_membership('admin'):
        return locals()
    else:
        redirect('view_customers')
@auth.requires_login() 
def view_one_dealer():
    dealer=db.DEALERS(request.args(0)) or redirect('view_dealers')
    return locals()



def email_invoice():
    bill=db.BILLS(request.args(0))
    context = dict(bill=bill)
    message = response.render('invoice.html', context)
    x=mail.send('the.budhiraja@gmail.com','Spencer\'s Bill {{=bill.id}} ',message=message)
    if x:
        redirect(URL('view_customers'))
    else:
        redirect(URL('bills'))
    
@auth.requires_login() 
def products():
    if auth.has_membership('admin'):
        return locals()
    else:
        redirect('view_products')
@auth.requires_login() 
def add_invoice():
    new_invoice=crud.create(db.BILLS,next='add_item_to_bill/[id]')
    return locals()
@auth.requires_login() 
def calc_bill():
    bill=db.BILLS(request.args(0))
    total=0
    billitems=db.BILLITEMS.bill==request.args(0)
    billitems=db(billitems)
    billitems=billitems.select()
    for i in billitems:
        total+=(i.product.mrp* ( 100 - i.product.discount) / 100 * i.quantity)
    net_total=total * 11/100 + total
    bill.update_record(total=total,net_total=net_total)
    redirect(URL('show_bill',args=bill.id))
@auth.requires_login() 
def bills():
    message=""
    message="Search Bill"
    if len(request.args):
        message=request.args(0)
        l=message.split('_')
        message=""
        for i in l:
            message+=i+' '
        message+='.Search again.\n'
    bills=db(db.BILLS).select(orderby=db.BILLS.id)
    form = SQLFORM.factory(Field('bill_id','integer',requires=IS_NOT_EMPTY()))
    if form.process(formname="form").accepted:
        redirect(URL('show_bill', args=(form.vars.bill_id)))
    elif form.errors:
        response.flash='Please re-enter'
    return locals()

@auth.requires_login() 
def show_bill():
    billid=request.args(0)
    bills=db.BILLS.id==request.args(0)
    bills=db(bills)
    bills=bills.select()
    if len(list(bills))==0:
        redirect(URL('bills',args='Requested Bill Not Found'))
    bill=db.BILLS(request.args(0))
    billitems=db.BILLITEMS.bill==request.args(0)
    billitems=db(billitems)
    billitems=billitems.select()
    return locals()

@auth.requires_login() 
def add_item_to_bill():
    billid=request.args(0)
    db.BILLITEMS.bill.default=request.args(0)
    new_billitem=crud.create(db.BILLITEMS,next=URL('add_item_to_bill',args=billid))
    return locals()


@auth.requires_login() 
def dealers():
    if auth.has_membership('admin'):
        return locals()
    else:
        redirect('view_dealers')

@auth.requires_login() 
def view_products():
    message=""
    message="Search a Product"
    if len(request.args):
        message=request.args(0)
        l=message.split('_')
        message=""
        for i in l:
            message+=i+' '
        message+='.Search again.\n'
    products=db(db.PRODUCTS).select(orderby=db.PRODUCTS.item_name)
    form1 = SQLFORM.factory(
        Field('products',requires=IS_IN_DB(db, 'PRODUCTS.id', '%(item_name)s')))
    if form1.process(formname="form_one").accepted:
        redirect(URL('view_product', args=(form1.vars.products)))
    elif form1.errors:
        response.flash = 'Product Not Found.Try Again.'
    form2 = SQLFORM.factory(
        Field('product_name',requires=IS_NOT_EMPTY()))
    if form2.process(formname="form_two").accepted:
        redirect(URL('searched_products', args=(form2.vars.product_name)))
    elif form2.errors:
         response.flash = 'Sorry.Please,Try Again'
    return locals()

@auth.requires_login() 
def view_customers():
    message=""
    message="Search a Customer"
    if len(request.args):
        message=request.args(0)
        l=message.split('_')
        message=""
        for i in l:
            message+=i+' '
        message+='.Search again.\n'
    form1 = SQLFORM.factory(
        Field('Customers',requires=IS_IN_DB(db, 'CUSTOMERS.id', '%(cust_name)s')))
    if form1.process(formname="form_one").accepted:
        redirect(URL('view_one_customer', args=(form1.vars.Customers)))
    customers=db(db.CUSTOMERS).select(orderby=db.CUSTOMERS.cust_name)
    customers=list(customers)
    form2 = SQLFORM.factory(
        Field('customer_name',requires=IS_NOT_EMPTY()))
    if form2.process(formname="form_two").accepted:
        redirect(URL('searched_customers', args=(form2.vars.customer_name)))
    elif form2.errors:
        response.flash = 'Customer Not Found.Try Again.'
    elif form2.errors:
         response.flash = 'Sorry.Please,Try Again'
    return locals()


@auth.requires_login() 
def searched_products():
    name=request.args(0)
    l=name.split('_')
    name2=""
    for i in l:
        name2+=i+' '
    name2=name2[:-1]
    form2 = SQLFORM.factory(
        Field('product_name',requires=IS_NOT_EMPTY(),default=name2))
    if form2.process(formname="form_two").accepted:
        redirect(URL('searched_products', args=(form2.vars.product_name)))
    query="SELECT * FROM PRODUCTS WHERE item_name LIKE '%"+name2+"%'"
    products=db.executesql(query)
    if len(products)<=0:
        redirect(URL('view_products',args="Product Not Found"))
    return locals()



@auth.requires_login() 
def searched_customers():    
    name=request.args(0)
    l=name.split('_')
    name2=""
    for i in l:
        name2+=i+' '
    name2=name2[:-1]
    form2 = SQLFORM.factory(
        Field('customer_name',requires=IS_NOT_EMPTY(),default=name2))
    if form2.process(formname="form_two").accepted:
        redirect(URL('searched_customers', args=(form2.vars.customer_name)))
    query="SELECT * FROM CUSTOMERS WHERE cust_name LIKE '%"+name2+"%'"
    customers=db.executesql(query)
    if len(customers)<=0:
        redirect(URL('view_customers',args="Customer Not Found"))
    return locals()

@auth.requires_login() 
def add_customer():
    new_customer = crud.create(db.CUSTOMERS, next='view_one_customer/[id]',message="New Customer Created.")
    return locals()

@auth.requires_login() 
def view_productsx():
    products=db(db.PRODUCTS).select(orderby=db.PRODUCTS.item_name)
    return locals()
@auth.requires_membership('admin') 
def add_product():
    new_product = crud.create(db.PRODUCTS, next='view_product/[id]',message="New Product Created")
    return locals()

def feedback():
    form = crud.create(db.FBACK, next='default',message="Feedback Recieved. Thank you!")
    return locals()
@auth.requires_membership('admin')
def view_feedback():
    fbacks=db(db.FBACK).select(orderby=db.FBACK.name)
    return locals()
@auth.requires_login()    
def gen_pdf():
    if len(request.args)==0:
        redirect(URL('bills'))
    bill=db.BILLS(request.args(0))
    billitems=db.BILLITEMS.bill==1
    billitems=db(billitems)
    billitems=billitems.select()
    html = response.render('default/invoice.html', dict(bill=bill,billitems=billitems))
    return plugin_appreport.REPORTPISA(html = html, title = 'my custom report using the plugin appreport')


@auth.requires_login() 
def view_dealers():
    dealers=db(db.DEALERS).select(orderby=db.DEALERS.dealer_name)
    return locals()

@auth.requires_membership('admin')
def add_dealer():
    new_dealer = crud.create(db.DEALERS, next='view_dealers')
    return locals()
@auth.requires_login() 
def view_product():
    product=db.PRODUCTS(request.args(0))
    return locals()
@auth.requires_login() 
def view_one_customer():
    customers=db.CUSTOMERS.id==request.args(0) or redirect(URL('view_customers',args="No Arguments"))
    customers=db(customers)
    customers=customers.select()
    if len(list(customers))==0:
        redirect(URL('view_customers',args="Customer Not Found"))
    bills=db.BILLS.customer==request.args(0)
    bills=db(bills)
    bills=bills.select()
    customer_total=0
    for i in bills:
        if i.net_total!=None:
            customer_total+=i.net_total
    customer=db.CUSTOMERS(request.args(0))
    return locals()
    
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
