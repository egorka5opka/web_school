from flask_restful import Resource, reqparse, abort
from flask import jsonify
from data.db_session import create_session
from data.history_events import HistoryEvent
from data.users import User


def abort_if_events_not_found(event_id):
    session = create_session()
    event = session.query(HistoryEvent).filter(HistoryEvent.id == event_id).first()
    session.close()
    if not event:
        abort(404, message=f"Событие с таким id не найдено")
    return event


parser = reqparse.RequestParser()
parser.add_argument('year', required=True, location='form', type=int)
parser.add_argument('event', location='form', type=str)
parser.add_argument('description', location='form', type=str)
parser.add_argument('user_id', required=True, location='form', type=int)


class HistoryEventRes(Resource):
    def get(self, event_id):
        event = abort_if_events_not_found(event_id)
        return jsonify({'success': 'OK', 'event': event.to_dict(only=('year', 'event', 'description'))})

    def delete(self, event_id):
        event = abort_if_events_not_found(event_id)
        session = create_session()
        session.delete(event)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    def post(self, event_id):
        args = parser.parse_args()
        event = abort_if_events_not_found(event_id)
        session = create_session()
        event.event = args['event']
        event.year = args['year']
        event.text = args['description']
        session.merge(event)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class HistoryListRes(Resource):
    def get(self):
        session = create_session()
        events = session.query(HistoryEvent).order_by(HistoryEvent.year).all()
        session.close()
        return jsonify([item.to_dict(only=('id', 'year', 'event', 'description', 'user_id')) for item in events])

    def post(self):
        session = create_session()
        args = parser.parse_args()
        user = session.query(User).get(args['user_id'])
        if not user:
            session.close()
            return jsonify({'success': 'failed',
                            'message': 'user not found'})
        event = HistoryEvent(year=args['year'],
                             event=args['event'],
                             text=args['description'])
        user.history_events.append(event)
        session.merge(user)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})
