# Hotler

Index your hotel and get an idea of what people say on it !

## Installation and usage

### Environment setup

create a virtualenv and install the required libs

```bash
$python -m venv venv
$source activate venv/bin/activate
$pip install -r requirements.txt
```

### IBM keys

Please set the `API_KEY` and `URL` of the service in the `Hotler/config.py` file.

### Run the server

You can run the server using

```bash
$python app.py
```

The server can then be access on your localhost on port `8080`

> the server link on localhost
>
> `http://127.0.0.1:8080/`

## Tone Analyzer

Get an overall score on the reviews for the given hotel

### Usage

to use the tone analyzer service, hit `/analyze/` endpoint with the hotel name as an argument as follows

`/analyzer/?q=HOTEL NAME`

you will get a json response in one of the following formats

1.on success

```json
{
  "status": "SUCCESS",
  "scores": {
    "anger": 0.515031,
    "fear": 0,
    "joy": 0.6710253499999999,
    "sadness": 0.5864978571428571
  }
}
```

2.fail due to new hotel that is not in the db

```json
{
  "status": "FAILED",
  "error": {
    "error_msg": "the hotel {hotel_name} doesn't exist."
  }
}
```

3.fail due to some ibm error

```json
{
  "status": "ERROR",
  "error": {
    "error_code": error_code,
    "error_msg": error_msg
  }
}
```

You can try these links as example

<a href="http://127.0.0.1:8080/analyze/?q=Hotel%20Roc%20Flamingo">Analyze hotel : Hotel Roc Flamingo</a>

<a href="http://127.0.0.1:8080/analyze/?q=Sheraton">Analyze hotel : Hotel Sheraton (which doesn't exist)</a>

## Hotel Indexer

Index all the hotels with their corresponding data.

To get started please add the elastic tokens in the `Hotler/config.py`, the keys we need are `ELASTIC_URL`, `ELASTIC_USERNAME` ,`ELASTIC_PASSWORD`.

You can use the `/index` endpoint to start indexing data in the elasticsearch db configured, this will start a background thread to load the data into an index called `hotels` and start to store data in it.

here is a sample of the stored data

```json
{
  "_shards": {
    "failed": 0,
    "skipped": 0,
    "successful": 1,
    "total": 1
  },
  "hits": {
    "hits": [
      {
        "_id": "u0U6UHABscdq1LZ_sMHo",
        "_index": "hotels",
        "_score": 1.0,
        "_source": {
          "branchs": {
            "Mableton": {
              "data": [
                {
                  "Unnamed: 0": 0,
                  "address": "Riviera San Nicol 11/a",
                  "categories": "Hotels",
                  "city": "Mableton",
                  "country": "US",
                  "latitude": 45.421611,
                  "longitude": 12.376187,
                  "name": "Hotel Russo Palace",
                  "postalCode": "30126",
                  "province": "GA",
                  "reviews.date": "2013-09-22T00:00:00Z",
                  "reviews.dateAdded": "2016-10-24T00:00:25Z",
                  "reviews.doRecommend": null,
                  "reviews.id": null,
                  "reviews.rating": 4.0,
                  "reviews.text": "Pleasant 10 min walk along the sea front to the Water Bus. restaurants etc. Hotel was comfortable breakfast was good - quite a variety. Room aircon didn't work very well. Take mosquito repelant!",
                  "reviews.title": "Good location away from the crouds",
                  "reviews.userCity": null,
                  "reviews.userProvince": null,
                  "reviews.username": "Russ (kent)"
                },
"tone": {
                "anger": 0,
                "fear": 0,
                "joy": 0.7093487333333333,
                "sadness": 0.612534625
              }
            }
          },
          "name": "Hotel Russo Palace",
          "tone": {
            "anger": 0.0,
            "fear": 0.0,
            "joy": 0.7093487333333333,
            "sadness": 0.612534625
          }
        },
        "_type": "_doc"
      }
    ],
    "max_score": 1.0,
    "total": {
      "relation": "eq",
      "value": 1
    }
  },
  "timed_out": false,
  "took": 2
}
```
