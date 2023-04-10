from flask import render_template, make_response, jsonify

from data_handler import get_event_by_id, get_events, get_fighter_data

def home():
    events = get_events()
    return render_template("home.html", events=events)

def event(id):
    event = get_event_by_id(id)
    return render_template("event.html", event=event)

def fighter(fighter_name):
    fighter = get_fighter_data(fighter_name)
    return make_response(jsonify(fighter))