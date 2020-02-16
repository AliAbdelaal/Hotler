from time import sleep
from threading import Thread
from flask import Flask, jsonify, request, render_template
from ibm_watson import ApiException
from Hotler.Analyzer import ToneAnalyzer
from Hotler.utils import DataLoader, Elastic

app = Flask(__name__)
analyzer = ToneAnalyzer()
data_loader = DataLoader()
elastic = Elastic()

def store_labled_docs(index, data):
    # label the data
    for doc in data:
        doc['tone'] = analyzer.analyze_text(doc['reviews.text'])
        # store it
        elastic.index_doc(index, doc)



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze/", methods=['GET'])
def analyze_hotel():
    # get the hotel
    hotel = request.args.get("q", default=None, type=str)
    # get the text for this hotel
    hotel_reviews = data_loader.get_hotel_reviews(hotel)
    status = None
    responce = {}
    if not hotel_reviews:
        # the hotel doesn't exist
        status = "FAILED"
        responce = {
            "status": status,
            "error": {
                "error_msg": f"the hotel {hotel} doesn't exist."
                }
        }
    else:
        # analyze the reviews
        try:
            scores = analyzer.analyze_text(hotel_reviews)
            status = "SUCCESS"
            responce = {
                "status": status,
                "scores": scores
            }
        except ApiException as ex:
            status = "ERROR"
            error_code = ex.code
            error_msg = ex.message
            responce = {
                "status": status,
                "error": {
                    "error_code": error_code,
                    "error_msg": error_msg
                }
            }
    return jsonify(responce)


@app.route("/index", methods=['GET'])
def index():
    # save all hotels in elastic
    # get all the data
    docs = data_loader.get_data_docs()
    # start saving the data in a separate thread in the background
    storing_job = Thread(target=store_labled_docs, args=("hotels", docs))
    storing_job.start()
    return jsonify({
        "status": "data is being stored in elasticsearch, you can get a quick look on the /list endpoint"
    })

@app.route("/list", methods=['GET'])
def list_some():
    # view sample docs
    elastic_res = elastic.get_docs("hotels")
    return jsonify(elastic_res)
