from collections import namedtuple
from random import choice
<<<<<<< HEAD
from flask import Flask, jsonify, url_for, request
from ecommerce import *
=======

from flask import Flask, jsonify
>>>>>>> d04365bf05b43932929b2086362ef4f13572f1b7

Quote = namedtuple("Quote", ("text", "author"))

quotes = [
    Quote("Talk is cheap. Show me the code.", "Linus Torvalds"),
    Quote("Programs must be written for people to read, and only incidentally for machines to execute.", "Harold Abelson"),
    Quote("Always code as if the guy who ends up maintaining your code will be a violent psychopath who knows where you live",
          "John Woods"),
    Quote("Give a man a program, frustrate him for a day. Teach a man to program, frustrate him for a lifetime.", "Muhammad Waseem"),
    Quote("Progress is possible only if we train ourselves to think about programs without thinking of them as pieces of executable code. ",
          "Edsger W. Dijkstra")
]

app = Flask(__name__)


@app.route("/quote", methods=["GET"])
def get_random_quote():
    return jsonify(choice(quotes)._asdict())

@app.route("/hello", methods=["GET"])
def hello():
<<<<<<< HEAD
   return "hello dream"

@app.route('/summary/<filter>.<format>', methods=['GET'])
def summary(filter, format):
    if request.method == 'GET':
        res = "."
        if format == "json":
            res = get_summary_json(filter)
        elif format == "html":
            res = get_summary_html(filter)
        return res
=======
    return "hello dream"
>>>>>>> d04365bf05b43932929b2086362ef4f13572f1b7
