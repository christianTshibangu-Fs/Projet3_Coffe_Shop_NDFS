import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,PATCH,DELETE,OPTIONS')
    return response

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()

    if not drinks:
        abort(404)

    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })












'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=["POST"])
#@requires_auth('post:drinks')
def create_drink():
    body = request.get_json()
    title = body.get("title",None)
    recipe = body.get("recipe",None)

    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except Exception:
        abort(422)
   
















'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id, payload):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
        abort(404)
    try:
        drink.title = body['title']
        drink.recipe = body['recipe']
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception:
        abort(422)













'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id, payload):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink.id
            })

    except Exception:
        abort(422)
        

       

# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
# Error Handler (404) Not Found
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

# Error Handler (401) Unauthorized
@app.errorhandler(AuthError)
def not_authenticated(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error
    }), 401

