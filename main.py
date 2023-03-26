#libraries for modal
import requests
import pandas as pd
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from textblob import TextBlob
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re

# libraries for fastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fake_useragent import UserAgent
from fastapi import HTTPException



app = FastAPI()
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# declaring header to access the html 
ua = UserAgent()
HEADERS = {'User-Agent': ua.random}


# defining the session storage to bypass the login redirect issue
session = requests.Session()
session.get("https://www.amazon.com/gp/sign-in.html")

class Review(BaseModel):
    url: str


@app.post("/analyze_review")
async def analyze_review(review: Review):
    result = {
        "GivenUrl": review.url,
        "PageStatus": "",
        "PageStatusString": "",
        "checkedPages": "",
        "NumberOfReviews": "",
        "NumberOfPOS": "",
        "NumberOfNEG": "",
        "AssumedProductQuality": "",
        "AnalysisResult": "",
        "Accuracy": ""
    }

    try:
        get_review_page(review.url, result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    response = {
        "GivenUrl": result["GivenUrl"],
        "PageStatus": result["PageStatus"],
        "PageStatusString": result["PageStatusString"],
        "checkedPages": result["checkedPages"],
        "NumberOfReviews": result["NumberOfReviews"],
        "NumberOfPOS": result["NumberOfPOS"],
        "NumberOfNEG": result["NumberOfNEG"],
        "AssumedProductQuality": result["AssumedProductQuality"],
        "AnalysisResult": result["AnalysisResult"],
        "Accuracy": result["Accuracy"]
    }

    return response

def get_review_page(url,result):    
    product_response = requests.get(url, headers=HEADERS)
    time.sleep(5)
    if product_response.status_code == 200:
        soup = BeautifulSoup(product_response.content, "html.parser")

        review_page_link = soup.find("a", {"data-hook": "see-all-reviews-link-foot"})
        new_link = review_page_link.get("href")
        getReviews(new_link,result)
    else:
        result["PageStatus"] = product_response.status_code
        result["PageStatusString"] = product_response.reason

  


# iterating through the Rieviews and pages
def getReviews(new_link,result):
    page_num = 1
    i=1
    parameters = ['Rating', 'Review']
    Review_Dataset = pd.DataFrame(columns=parameters)
    while True:
        page_url =  'https://www.amazon.in' + new_link + '&pageNumber=' + str(page_num)
        reviewPageResponse = session.get(page_url,headers=HEADERS)
        if reviewPageResponse.status_code == 200  :
            result["PageStatus"]=200
            soup2 = BeautifulSoup(reviewPageResponse.content, "html.parser")
            page_reviews = soup2.find_all("div", {"class": "a-section celwidget"})

            if len(page_reviews) > 0:
                for review in page_reviews:
                    review_text = review.find("span", {"class": "a-size-base review-text review-text-content"}).text.strip()
                    rating = review.find("span", {"class":"a-icon-alt"}).text[:3]
                    data = pd.DataFrame([rating,review_text], columns=[i], index=parameters).T
                    Review_Dataset = pd.concat((Review_Dataset, data)) 
                    i+=1
                page_num +=1 
            else:
                result["checkedPages"]=page_num
                result["NumberOfReviews"]=len(Review_Dataset.index)
                break                    
        else:
            result["PageStatus"]=reviewPageResponse.status_code
            result["PageStatusString"]=reviewPageResponse.reason
            break       
    prediction = GetBuyingPrediction(Review_Dataset,result)
    GetAccuracyScore(Review_Dataset,result)
    result["AnalysisResult"]=prediction




# Making the prediction 
def GetBuyingPrediction(Dataset,result):
    #print(Dataset)
    Dataset['sentiment'] = Dataset['Review'].apply(get_sentiment)
    avg_sentiment_score = Dataset['sentiment'].mean()
    result["AssumedProductQuality"]=str(round(avg_sentiment_score*100, 2)) + "%"
    print(str(avg_sentiment_score*100) + "%")
    print(avg_sentiment_score)
    if avg_sentiment_score >= 0.5:
        return "I recommend investing in the product as it would be a beneficial use of your money."
    elif avg_sentiment_score >= 0.3:   
        return "It might be worth considering investing in the product, but make sure to weigh the potential benefits and risks before making a decision."
    else:
        return "I would suggest against investing in this product" 


def get_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    return 1 if sentiment > 0 else 0



def GetAccuracyScore(Dataset,result):
    vectorizer = CountVectorizer()
    logreg = LogisticRegression()

    Dataset['Review'] = Dataset['Review'].apply(preprocess_text)

    # dividing data in ratio of 25 and 75
    X_train, X_test, y_train, y_test = train_test_split(Dataset['Review'], Dataset['sentiment'], random_state=0)

    X_train_transformed = vectorizer.fit_transform(X_train)

    logreg.fit(X_train_transformed, y_train)

    X_test_transformed = vectorizer.transform(X_test)

    y_pred = logreg.predict(X_test_transformed)

    result["Accuracy"]=str(float(accuracy_score(y_test, y_pred)*100)) + "%"  
    result["NumberOfPOS"] = str(len(Dataset[Dataset['sentiment'] == 1]))
    result["NumberOfNEG"] = str(len(Dataset[Dataset['sentiment'] == 0]))




def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    tokens = word_tokenize(text)

    new_tokens=[]
    for token in tokens:
        if token not in stop_words:
            token = lemmatizer.lemmatize(token)
            new_tokens.append(token)

    text = ' '.join(new_tokens)
    return text



