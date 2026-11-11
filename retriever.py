import json
import re
from difflib import get_close_matches
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

EXTRA_STOP = {"plant", "plants", "herb", "herbs", "take", "taking", "intake",
              "reduce", "reduces", "relief", "remedy", "good", "best", "help",
              "use", "using", "feel", "feeling", "got", "tell", "want", "need"}
STOP_WORDS = list(ENGLISH_STOP_WORDS | EXTRA_STOP)
STOP_SET = set(STOP_WORDS)

SYN = {"tummy": "stomach ache", "belly": "stomach ache", "sneezing": "cold",
       "runny": "cold", "nose": "cold", "tired": "fatigue", "tiredness": "fatigue",
       "sugar": "blood sugar", "bp": "blood pressure", "pressure": "blood pressure",
       "period": "period cramps", "periods": "period cramps",
       "sleepless": "insomnia", "pimple": "pimples", "gastric": "acidity",
       "vomit": "vomiting", "memory": "poor memory", "focus": "low focus",
       "burn": "burns", "hairfall": "hair fall"}

MIN_SCORE = 0.05


class HerbRetriever:
    def __init__(self, path="herbs.json"):
        self.herbs = []
        for p in (path, "herbs_more.json"):
            try:
                with open(p, encoding="utf-8") as f:
                    self.herbs += json.load(f)
            except FileNotFoundError:
                pass
        self.vectorizer = TfidfVectorizer(
            stop_words=STOP_WORDS, ngram_range=(1, 2), lowercase=True
        )
        texts = [self._text(h) for h in self.herbs]
        self.matrix = self.vectorizer.fit_transform(texts)
        names = self.vectorizer.get_feature_names_out()
        self.vocab_list = [w for w in names if " " not in w]
        self.vocab = set(self.vocab_list)
        self.symptom_vocab = {w for h in self.herbs for s in h["symptoms"] for w in s.lower().split()}

    @staticmethod
    def _text(herb):
        s = " ".join(herb["symptoms"])
        return f'{herb["name"]} {s} {s} {s} {herb["uses"]}'

    def analyze(self, query):
        out, matched = [], []
        for token in re.findall(r"[a-z]+", query.lower()):
            if token in STOP_SET:
                continue
            for w in SYN.get(token, token).split():
                if w not in self.vocab and len(w) >= 5:
                    close = get_close_matches(w, self.vocab_list, n=1, cutoff=0.78)
                    if close and close[0][0] == w[0]:
                        w = close[0]
                out.append(w)
                if w in self.vocab and w not in matched:
                    matched.append(w)
        return " ".join(out), matched

    def search(self, query, top_k=3):
        cleaned, _ = self.analyze(query)
        if not cleaned.strip():
            return []
        scores = cosine_similarity(self.vectorizer.transform([cleaned]), self.matrix)[0]
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [{"score": round(float(scores[i]), 3), "herb": self.herbs[i]}
                for i in ranked[:top_k] if scores[i] >= MIN_SCORE]