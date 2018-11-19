#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

from flask import jsonify, request, url_for, g
from flask.views import MethodView

from app.apis.v1 import api_v1
from app.apis.v1.auth import generate_token, auth_required
from app.apis.v1.errors import api_abort
from app.models.auth import User


class IndexAPI(MethodView):

    def get(self):
        return jsonify({
            "api_version": "1.0",
            "api_base_url": url_for('.index', _external=True),
            "authentication_url": url_for('.token', _external=True),
            "user_url": url_for('.user', _external=True)
        })


api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])


class AuthTokenAPI(MethodView):

    def post(self):
        grant_type = request.form.get('grant_type')
        email = request.form.get('email')
        password = request.form.get('password')

        if grant_type is None or grant_type.lower() != 'password':
            return api_abort(code=400, message='The grant type must be password.')

        user = User.query.filter_by(email=email).first()
        if user is None or not user.verify_password(password):
            return api_abort(code=400, message='Either the username or password was invalid.')

        token, expiration = generate_token(user)

        response = jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': expiration
        })
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response


api_v1.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['POST'])


class UserAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        return jsonify({
            'url': url_for('api_v1.user', _external=True),
            'username': g.current_user.username
        })


api_v1.add_url_rule('/user', view_func=UserAPI.as_view('user'), methods=['GET'])
