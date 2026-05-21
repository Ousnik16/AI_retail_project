from transformers import pipeline

class ReviewSentimentAnalyzer:
    def __init__(self):
        self.pipeline = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

    def analyze(self, texts):
        return self.pipeline(texts)
