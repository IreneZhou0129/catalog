# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Category, Item, User
from flask import session as login_session
import random
import os
import string

import httplib2
import json

from flask import make_response

from helper import login_status_verification, not_authorized_alert


# Alert for user not authorized to access given API
not_authorized_alert = not_authorized_alert()

app = Flask(__name__)

# Connect to the Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

session = scoped_session(sessionmaker(bind=engine))


# ==============================
# JSON EndPoint all data
# ==============================


@app.route('/users_json')
def userJSON():
    '''Api end points for all jsonify Users'''

    users = session.query(User).all()
    return jsonify(User=[u.serialize for u in users])


# API endpoints for all categories and items.
@app.route('/category_json')
def categoriesJSON():
    '''Api end points for all jsonify categories'''

    catelog = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in catelog])


# API endpoints for all items.
@app.route('/items_json')
def itemsJSON():
    '''Api end points for all jsonify Items'''

    categories = session.query(Category).all()
    items = session.query(Item).all()
    return jsonify(
        Categories=[
            c.serialize for c in categories], Items=[
            i.serialize for i in items])


# ======================================
# CRUD for User
# ref https://github.com/udacity/ud330/blob/master/Lesson4/step2/project.py
# ======================================
def getUserID(email):
    '''Helper function for obtaining user_id for facebook login'''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


def getUserInfo(user_id):
    '''Helper function for obtaining user by id '''
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    '''Helper function for in case the login user is not in the database'''
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
    )
    session.add(newUser)
    session.commit()

    user = session.query(User).filter_by(email=login_session['email']).one()

    return user.id


# ======================================
# CRUD for categories
# ======================================
@app.route('/')
@app.route('/categories')
def getCategory():
    '''API endPoints for get categories or HOME page'''
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.item_id.desc())
    quantity = items.count()

    rendering_template = 'category.html'

    # if user is not login is disable for adding  , editing and deleting
    if 'user_id' not in login_session:
        rendering_template = 'public_category.html'

    return render_template(
        rendering_template,
        categories=categories,
        quantity=quantity,
        items=items)


@app.route('/category/new', methods=['GET', 'POST'])
@login_status_verification
def createCategory():
    '''API endPoints for create categories'''
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                              user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()

        categories = session.query(Category).filter_by(
            user_id=login_session['user_id']).all()

        # notify user for the update
        flash("Adding new category", "success")
        return redirect(url_for('getCategory', categories=categories))

    else:
        return render_template('category_add.html')


# DELETE a category
@app.route('/categories/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    """Allows user to delete an existing category"""
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()

    if categoryToDelete.user_id != login_session['user_id']:
        return not_authorized_alert

    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(
            url_for('getCategory', category_id=category_id))
    else:
        return render_template(
            'category_delete.html', category=categoryToDelete)


@app.route('/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
def updateCategory(category_id):
    """Allows user to edit an existing category"""
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    # user not login
    if editedCategory.user_id != login_session['user_id']:
        return not_authorized_alert

    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            session.commit()
            flash(
                'Category Successfully Edited %s' %
                editedCategory.name, 'success')
            return redirect(url_for('getCategory'))
    else:
        return render_template('category_edit.html', category=editedCategory)


# ======================================
# CRUD for Items
# ======================================
# GetItems for each category have multiple Items
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items/')
def getItems(category_id):
    """returns items in category"""
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).all()  # why do we need this
    items = session.query(Item).filter_by(category_id=category_id)
    quantity = items.count()
    return render_template(
        'category_items.html', categories=categories,
        category=category, items=items,
        quantity=quantity,)


# Obtain Speific Catgory Item
@app.route('/categories/<int:category_id>/item/<int:category_item_id>/')
def getCategoryItem(category_id, category_item_id):
    """obtain specific category and specific item"""
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()

    item = session.query(Item).filter_by(item_id=category_item_id).one()

    creator = session.query(User).filter_by(id=item.user_id).one()

    return render_template(
        'item.html', category=category,
        item=item, creator=creator,
        categories=categories)


# CREATE ITEM
@app.route('/categories/item/new', methods=['GET', 'POST'])
@login_status_verification
def createItem():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.item_id.desc())
    quantity = items.count()
    if request.method == 'POST':
        addNewItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form.get("comp_select"),
            user_id=login_session['user_id'])

        session.add(addNewItem)
        session.commit()
        return redirect(url_for('getCategory'))
    else:
        return render_template('item_add.html',
                               categories=categories,
                               quantity=quantity,
                               items=items,
                               flag=True)


# CREATE ITEM
@app.route('/categories/<int:category_id>/item/new', methods=['GET', 'POST'])
@login_status_verification
def createCategoryItem(category_id):
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.item_id.desc())
    quantity = items.count()

    if request.method == 'POST':
        addNewItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=category_id,
            user_id=login_session['user_id'])
        session.add(addNewItem)
        session.commit()
        return redirect(url_for('getCategory'))
    else:
        return render_template('item_add.html',
                               categories=categories,
                               quantity=quantity,
                               items=items,
                               condition=False)


# UPDATE ITEM
@app.route(
    '/categories/<int:category_id>/item/<int:category_item_id>/edit',
    methods=[
        'GET',
        'POST'])
@login_status_verification
def updateCategoryItem(category_id, category_item_id):
    """return "This page will be for making a updating catalog item" """
    editingItem = session.query(Item).filter_by(item_id=category_item_id).one()

    if editingItem.user_id != login_session['user_id']:
        return not_authorized_alert

    if request.method == 'POST':
        if request.form['name']:
            editingItem.name = request.form['name']
        if request.form['description']:
            editingItem.description = request.form['description']
        if request.form['category']:
            editingItem.category = request.form['category']

        session.add(editingItem)
        session.commit()
        flash("Item %s updated!" % editingItem.name, 'success')
        return redirect(url_for('getCategory'))
    else:
        categories = session.query(Category).all()
        return render_template(
            'item_edit.html',
            categories=categories,
            item=editingItem)


# DELETE ITEM
@app.route(
    '/categories/<int:category_id>/item/<int:category_item_id>/delete',
    methods=[
        'GET',
        'POST'])
@login_status_verification
def deleteCategoryItem(category_id, category_item_id):
    """return "This page will be for deleting a catalog item" """
    itemToDelete = session.query(
        Item).filter_by(item_id=category_item_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>" 
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('deleted category item %s' % itemToDelete.name, 'success')
        return redirect(url_for('getCategory'))
    else:
        return render_template(
            'item_delete.html', item=itemToDelete)

# ======================================
# Login
# ref https://github.com/udacity/ud330/blob/master/Lesson4/step2/project.py
# ======================================


@app.route('/login')
def showLogin():
    """ Generate state for login status  """

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# ======================================
# FaceBook Login
# ref https://github.com/udacity/ud330/blob/master/Lesson4/step2/project.py
# ======================================
# Connect FB login

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(
        open(
            'fb_client_secrets.json',
            'r').read())['web']['app_id']
    app_secret = json.loads(
        open("fb_client_secrets.json", 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secrets=%s&fb_exchange_token=%s' % ( 
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.8/me?fields=id%2Cname%2Cemail%2Cpicture&access_token=' + access_token 
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]

    login_session['email'] = data["email"]
    login_session['user_id'] = getUserID(login_session['email'])
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session
    # in order to properly logout
    login_session['access_token'] = access_token

    # Get user picture
    login_session['picture'] = data["picture"]["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''''
    <h1>Welcome , %s!</h1>
    <img src="%s"
        style = "width: 300px; height: 300px;
                border-radius: 150px;
                -webkit-border-radius: 150px;
                -moz-border-radius: 150px;"/>
    ''' % (login_session['username'], login_session['picture'])

    flash("Now logged in as %s" % login_session['username'], 'success')
    return output


# disconnect FB login
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/disconnect')
def disconnect():

    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        if 'username' in login_session:
            del login_session['username']
        if 'email' in login_session:
            del login_session['email']
        if 'picture' in login_session:
            del login_session['picture']
        if 'user_id' in login_session:
            del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.", 'success')
        return redirect(url_for('getCategory'))
    else:
        flash("You were not logged in", 'danger')
        return redirect(url_for('getCategory'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=port)
