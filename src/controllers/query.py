"""
Controller for survey searches.
"""

import logging
import uuid
from typing import Dict, Union

import flask_restplus as FRP
from flask import request, Response, jsonify
from redis import Redis
from rq import Queue

from models.query import App
import services.query as service
from tasks import RQueues
from tasks.query import catch_moving_target
from util import jsonify_output

API: FRP.Namespace = App.api

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/moving")
class Query(FRP.Resource):
    """Controller class for CATCH queries of moving targets."""

    @API.doc('--query/moving--')
    @API.param(
        'target', _in='query',
        description='Search for this moving target.'
    )
    @API.param(
        'source', _in='query',
        description='Search this observation source or "any".'
    )
    @API.param(
        'cached', _in='query',
        description='Return cached results, if available.'
    )
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'Query') -> Response:
        """Query for moving target."""

        # Extract params from URL
        query: Dict[str, Union[str, bool]] = {
            'target': request.args.get('target', '', str),
            'source': request.args.get('source', 'any', str),
            'cached': request.args.get('cached', True, FRP.inputs.boolean)
        }

        # Connect to started-jobs queue
        conn = Redis.from_url('redis://')
        queue = Queue(RQueues.START_JOBS, connection=conn)
        total_jobs = len(queue.jobs)

        # Build immediate response
        response: Response
        if total_jobs > 100:
            response = jsonify({
                "message": "Error: queue is full."
            })
            response.status_code = 200
        else:
            # unique job ID
            job_id: uuid.UUID = uuid.uuid4()

            cached = False
            if query['cached']:
                # check Catch Queries cache for previous search results
                cached = service.check_cache(query['target'], query['source'])

            if cached:
                # return cached results
                data = service.query(query['target'], job_id,
                                     source=query['source'],
                                     cached=True)
                response = jsonify({
                    "message": "Returning cached results.",
                    "query": query,
                    "count": len(data),
                    "job_id": job_id.hex,
                    "data": FRP.marshal(data, App.caught_data)
                })
                response.status_code = 200
            else:
                # Spin out task to worker, return job_id
                queue.enqueue(catch_moving_target, query['target'],
                              query['source'], query['cached'], job_id)
                response = jsonify({
                    "message": "Enqueued search.",
                    "query": query,
                    "job_id": job_id.hex
                })
                response.status_code = 200

        return response


@API.route("/moving/labels")
class QueryMovingLabels(FRP.Resource):
    """Controller for query caught moving object column labels."""

    @API.doc('--query/moving/labels--')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    def get(self: 'QueryMovingLabels') -> Dict[str, Dict[str, str]]:
        """Query caught moving object table labels."""
        data: Dict[str, Dict[str, str]] = (
            service.column_labels('/moving'))
        return data
