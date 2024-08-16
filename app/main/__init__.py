from flask import Blueprint
import logging
import stripe
logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)
from . import routes