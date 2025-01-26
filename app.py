from requests import post as rpost
from json import loads as json
from flask import Flask, render_template, request, jsonify

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from logging import error as log_error, info as log_info, warning as log_warning, critical as log_critical, debug as log_debug
from coloredlogs import install as cloginstall
from verboselogs import VerboseLogger, VERBOSE

CHATBOT_API_KEY = "BwYLppC6tQ7t2fegk5xi57ZncG4pRPYlNVHqfX20pkqEj4JYI6aqJQQJ99BAACYeBjFXJ3w3AAAaACOGj3Fi"
CHATBOT_API_URL = "https://chatbot-model.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=local-business-ai&api-version=2021-10-01&deploymentName=production"

LANGUGAE_API_KEY = "19O3s8nmaOUhKCoskZ3UEYMZvVZxdqpYqogJSz3y3A1ZYQJ1qkoSJQQJ99BAACYeBjFXJ3w3AAAaACOGsRzF"
LANGUGAE_API_URL = "https://chatbot-model.cognitiveservices.azure.com/"

app = Flask(__name__, static_folder='static')
logger = VerboseLogger('my_logger')
cloginstall(level=VERBOSE, fmt='[%(asctime)s] | %(levelname)-6s | %(message)s')

class chatbot():
    def __init__(self, API_KEY, API_URL):
        self.API_KEY = API_KEY
        self.API_URL = API_URL
    
    def chat(self, query):
        body = {
            "top":3,
            "question": query,
            "includeUnstructuredSources":True,
            "confidenceScoreThreshold":0.5,
            "answerSpanRequest":{
                "enable":True,
                "topAnswersWithSpan":1,
                "confidenceScoreThreshold":0.5
            },
            "filters":{
                "metadataFilter":{"logicalOperation":"OR",
                    "metadata":[]
                }
            }
        }

        headers = {
        "Ocp-Apim-Subscription-Key": self.API_KEY,
        "Content-Type": "application/json"
        }

        response = rpost(self.API_URL, headers=headers, json=body)
        if response.status_code == 200:
            return json(response.text)["answers"][0]["answer"]
        else:
            return "Server Not Responding!"

class sentiment_analysis():
    def __init__(self, API_KEY, API_URL):
        self.API_KEY = API_KEY
        self.API_URL = API_URL
        self.client = self.authenticate_client()

    def authenticate_client(self):
        ta_credential = AzureKeyCredential(self.API_KEY)
        text_analytics_client = TextAnalyticsClient(
                endpoint=self.API_URL, 
                credential=ta_credential)
        return text_analytics_client


    def analysis(self, query):
        documents = [query]
        result = self.client.analyze_sentiment(documents, show_opinion_mining=True)
        query_result = [doc for doc in result if not doc.is_error]
        return query_result


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/products-details')
def products_details():
    return render_template('products-details.html')

@app.route('/accounts')
def accounts():
    return render_template('accounts.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query')
    bot = chatbot(CHATBOT_API_KEY, CHATBOT_API_URL)
    response = {'reply': bot.chat(query)}
    return response

@app.errorhandler(Exception)
def page_not_found(e):
    return f"<h1>Unexpected Error!</h1><br><h2>{e}</h2>", 404


if __name__ == '__main__':
    app.run(debug=True, port="5000")
    