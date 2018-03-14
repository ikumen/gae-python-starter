import logging

from flask import Blueprint, jsonify, request, Response
from ..models import User

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/users', methods=['get'])
def api_list_users():
   """
   Handles request for listing all users.
   """
   return jsonify(User.list())


@bp.route('/users', methods=['post'])
def api_create_user():
   """
   Handle creating a new user.
   """
   data = request.get_json()
   return jsonify(User.create(**data))
