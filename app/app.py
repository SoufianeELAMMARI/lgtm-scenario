import logging
import random
import time

from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("demo-app")

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(status="ok", service="demo-app")


@app.route("/rolldice")
def rolldice():
    # simulate some work -> shows up as span duration + latency metric
    time.sleep(random.uniform(0.01, 0.30))
    roll = random.randint(1, 6)

    # ~10% of requests fail -> this is what makes the SLO / error budget move
    if random.random() < 0.10:
        logger.error("payment processing failed for roll=%s", roll)
        return jsonify(error="internal error"), 500

    logger.info("rolled a %s", roll)
    return jsonify(roll=roll)


@app.route("/slow")
def slow():
    # an occasional slow path -> useful for latency panels and trace inspection
    time.sleep(random.uniform(0.5, 1.5))
    logger.warning("slow path was hit")
    return jsonify(status="slow-ok")
