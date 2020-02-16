from time import sleep
from threading import Thread
import numpy as np
from flask import Flask, jsonify, request, render_template
from ibm_watson import ApiException
from Hotler.Analyzer import ToneAnalyzer
from Hotler.utils import DataLoader, Elastic

app = Flask(__name__)
analyzer = ToneAnalyzer()
data_loader = DataLoader()
elastic = Elastic()

def store_labled_docs(index, data):
    """for each hotel, find it's branches and calculate the scores in the database
    
    Arguments:
        index {str} -- the index to store data in
        data {pd.DataFrame} -- the input frame to load data from
    """
    # get list of all the unique names
    names = data.name.unique()
    for name in names:
        doc = {"name": name, "branchs": {}}
        # get list of all branchs by city
        local_data = data.loc[data.name==name, :]
        # aggregate of scores for this hotel
        scores = []
        cities = local_data.city.unique()
        for city in cities:
            # create the key for this city
            doc['branchs'][city] = {}
            # calculate the score on this city
            doc['branchs'][city]['data'] = local_data.loc[local_data.city==city, :].to_dict("records")
            city_score = analyzer.analyze_text(".".join(local_data.loc[local_data.city==city, "reviews.text"].values))
            scores.append(city_score)
            doc['branchs'][city]['tone'] = city_score
        doc['tone'] = {}
        for key in scores[0].keys():
            doc['tone'][key] = np.mean([i[key] for i in scores])
        
        # store the doc of the hotel
        elastic.index_doc(index, doc)

    # # aggregate on the same hotel
    # scanned = []
    # # label the data
    # for doc in data:
    #     hotel_name = doc['name']
    #     if hotel_name in scanned:
    #         pass
    #     else:
    #         doc['tone'] = analyzer.analyze_text(doc['reviews.text'])
    #         # store it
    #         elastic.index_doc(index, doc)



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
    data = data_loader.get_data()
    # start saving the data in a separate thread in the background
    storing_job = Thread(target=store_labled_docs, args=("hotels", data))
    storing_job.start()
    return jsonify({
        "status": "data is being stored in elasticsearch, you can get a quick look on the /list endpoint"
    })

@app.route("/list", methods=['GET'])
def list_some():
    # view sample docs
    try:
        elastic_res = elastic.get_docs("hotels")
        return jsonify(elastic_res)
    except Exception as ex:
        return jsonify({"error":"the index is not yet created, there may be an error or the index was not yet created!"})
