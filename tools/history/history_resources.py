from flask_restful import Resource, reqparse, abort
from flask import jsonify
from data.db_session import create_session
from data.history_events import HistoryEvent


def abort_if_events_not_found(event_id):
    session = create_session()
    events = session.query(HistoryEvent).get(event_id)
    if not events:
        abort(404, message=f"Events {event_id} not found")


class HistoryEventRes(Resource):
    def get(self, event_id):
        abort_if_events_not_found(event_id)
        session = create_session()
        event = session.query(HistoryEvent).get(event_id)
        return jsonify({'event': event.to_dict(only=('id', 'year', 'event', 'description'))})

    def delete(self, event_id):
        abort_if_events_not_found(event_id)
        session = create_session()
        event = session.query(HistoryEvent).get(event_id)
        session.delete(event)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('year', required=True, location='form', type=int)
parser.add_argument('event', location='form', type=str)
parser.add_argument('description', location='form', type=str)


class HistoryListRes(Resource):
    def get(self):
        session = create_session()
        events = session.query(HistoryEvent).all()
        return jsonify({'events': [item.to_dict(only=('id', 'year', 'event')) for item in events]})

    def post(self):
        session = create_session()
        args = parser.parse_args()
        HistoryEvent(year=args['year'],
                     event=args['event'],
                     text=args['description'])
        session.add(HistoryEvent)
        session.commit()
        return jsonify({'success': 'OK'})
