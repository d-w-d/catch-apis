
"""
Demo Routes Module
Just a bunch of simple routes that you can reference/copy to start developing new routes
"""


import logging
from typing import Dict, Union, Any, List
import flask_restplus as FRP
from flask import request, wrappers as FLW
from models.query import App
from services.name_search import name_search
from util import jsonify_output

API: FRP.Namespace = App.api

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/name")
class NameSearch(FRP.Resource):
    """Controller class for testing target names."""

    @API.doc('--search/name--')
    @API.param(
        'name', _in='query',
        description='Target name to search for.'
    )
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    @API.marshal_with(App.search_name_model)
    def get(self: 'NameSearch') -> Dict[str, Union[str, dict]]:
        """Search moving target name."""

        name: str = request.args.get('name', '', str)
        top_matches: dict = name_search(name)

        response: Dict[str, Union[str, dict]] = (
            {
                'name': name,
                'matches': top_matches
            }
        )
        return response
