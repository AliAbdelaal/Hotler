import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from Hotler import config

class ToneAnalyzer:

    def __init__(self):
        # read the keys from your system and initialize connection
        authenticator = IAMAuthenticator(config.APIKEY)
        self.__tone_analyzer = ToneAnalyzerV3(
            version='2017-09-21',
            authenticator=authenticator
        )

        self.__tone_analyzer.set_service_url(config.URL)


    def analyze_text(self, text): 
        """analyze the given text sentences and aggregate the results
        
        Arguments:
            text {str} -- the input text            

        Returns:
            dict -- the aggregated result {'anger': 0, 'fear': 0, 'joy': 0, 'sadness': 0}
        """
        # the supported emotions
        emotions = ["anger", "fear", "joy", "sadness"]

        # request the analysis from watson
        tone_analysis = self.__tone_analyzer.tone({'text': text},
        content_type='application/json').get_result()



        # if there's no score for the sentences see the overall tone
        if not tone_analysis.get('sentences_tone', None):
            scores = dict.fromkeys(emotions, 0)
            for tone in tone_analysis['document_tone']['tones']:
                if tone['tone_id'] in emotions:
                    scores[tone['tone_id']] += tone['score']
            return scores

        # count the results from sentences
        scores = dict.fromkeys(emotions, [])
        for sentence in tone_analysis['sentences_tone']:
            for tone in sentence['tones']:
                if tone['tone_id'] in emotions:
                    if scores.get(tone['tone_id'], None):
                        scores[tone['tone_id']].append(tone['score'])
                    else:
                        scores[tone['tone_id']] = [tone['score']]
        # normalize the results
        for key in scores:
            if not scores[key]:
                scores[key]=  0
            else:
                scores[key] = sum(scores[key])/len(scores[key])
        return scores
