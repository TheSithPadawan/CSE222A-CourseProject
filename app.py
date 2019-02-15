from flask import Flask
from flask import request
import requests
from flask import Response
from server import create_app, db
from server.model.college import CollegeModel
from flask import json
import numpy as np

"""
benchmark on 2 things
1) server response time 
2) server load 
"""
api_key = "RTfzWBrrZbwSHNhtqHVFRZbNu1EfuvlW2txAExTB";
app = create_app()
my_lucky_numbers = set()
my_lucky_numbers.add(5)
my_lucky_numbers.add(8)

def hello_world(name):
    url = "https://api.data.gov/ed/collegescorecard/v1/schools?school.name="+name+"&api_key=RTfzWBrrZbwSHNhtqHVFRZbNu1EfuvlW2txAExTB"
    url += "&api_key="+api_key
    r = requests.get(url)
    return r

@app.route('/get_school')
def get_school():
    name = request.args.get('name')
    num = np.random.randint(10)
    if num in my_lucky_numbers:
        r = hello_world(name)
        response = Response(r.text, r.status_code)
        return response
    else:
        school = CollegeModel.find_by_school_name(name)
        response = app.response_class(
            response=json.dumps(school.json()),
            status=200,
            mimetype='application/json'
        )
        return response

if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        app.run(Threaded=True)
