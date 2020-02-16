import os 
import pandas as pd
import numpy as np
from elasticsearch import Elasticsearch
from Hotler import config

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "hotels.csv")


class DataLoader():

    def __init__(self):
        self.__data = pd.read_csv(DATA_DIR)


    def get_hotel_reviews(self, hotel_name)->str:
        """get all the text reviews for this specific hotel
        
        Arguments:
            hotel_name {str} -- name of the targeted hotel
        
        Returns:
            text -- all the reviews concatinated toegether in one string
        """
        text = ".".join(self.__data.loc[self.__data.name == hotel_name, "reviews.text"].values)
        return text
    
    def get_data_docs(self)->list:
        """get all the data in the file in form of list of dictionaries
        
        Returns:
            list -- list of docs
        """

        return self.__data.replace({np.nan: None}).to_dict("records")


class Elastic():

    def __init__(self):
        self.__es = Elasticsearch([config.ELASTIC_URL],
        http_auth=(config.ELASTIC_USERNAME, config.ELASTIC_PASSWORD))
        # make sure everything works
        if not self.__es:
            raise Exception("Couldn't connect to elastic search instance, check your keys")
    
    def index_docs(self, index, docs):
        """store the given docs in the specified index
        
        Arguments:
            index {str} -- the index to store data in
            docs {list} -- list of dict of the document to store
        """
        for doc in docs:
            self.__es.index(index=index, body=doc)
    
    def index_doc(self, index, doc):
        """store doc in index
        
        Arguments:
            index {str} -- the index to store data in
            doc {dict} -- the doc to save
        """
        self.__es.index(index=index, body=doc)

    def get_docs(self, index)->list:
        """read all docs from specific index
        
        Arguments:
            index {str} -- the index to read from
        
        Returns:
            list -- list of docs
        """
        return self.__es.search(index=index)