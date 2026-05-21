import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentRecommender:
    def __init__(self, products):
        self.products = products
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.matrix = self.vectorizer.fit_transform([self._combine_metadata(p) for p in products])

    def _combine_metadata(self, product):
        return ' '.join([product.get('name', ''), product.get('category', ''), ' '.join(product.get('tags', []))])

    def recommend_similar(self, product_id, top_n=5):
        index = next((i for i, item in enumerate(self.products) if item['id'] == product_id), None)
        if index is None:
            return []
        scores = cosine_similarity(self.matrix[index:index+1], self.matrix).flatten()
        indices = np.argsort(scores)[::-1][1:top_n+1]
        return [self.products[i] for i in indices]
