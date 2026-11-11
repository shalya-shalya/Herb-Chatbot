import random
import re
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from retriever import HerbRetriever

app = FastAPI(title="Herbal Guide")
retriever = HerbRetriever("herbs.json")
app.mount("/static", StaticFiles(directory="static"), name="static")


class Chat(BaseModel):
    message: str


GREET = re.compile(r"^\s*(hi+|hello+|hey+|namaste|good (morning|afternoon|evening)|how are you)\b", re.I)
THANKS = re.compile(r"\b(thanks|thank you|thx|tq)\b", re.I)
BYE = re.compile(r"^\s*(bye|goodbye|see you|ok bye)\b", re.I)
ABOUT = re.compile(r"\b(who are you|what can you do|what do you do|help me use)\b", re.I)
RED = re.compile(r"chest pain|can.?t breathe|difficulty breathing|unconscious|seizure|stroke|heavy bleeding|"
                 r"poison|overdose|suicid|kill myself|self.?harm|want to die|worst headache", re.I)

OPENERS = ["Oh, sorry you’re dealing with {t}.", "Hmm, {t} can be really annoying.",
           "I’m sorry to hear about the {t}.", "Let’s see what might help with {t}."]
CLOSERS = ["Hope you feel better soon! 🌿 If it lasts more than a few days, or you take regular medicines, please check with a doctor first.",
           "Take care of yourself! 🌿 If it doesn’t improve in a few days, or you’re on any medicines, please see a doctor first.",
           "Wishing you a quick recovery! 🌿 Please check with a doctor if it continues, or if you take regular medicines."]


def reply(msg):
    if RED.search(msg):
        return {"reply": "This sounds serious, and I care that you get proper help. 💚 Please call emergency services (112 in India) or see a doctor right away instead of using herbs. If you are thinking of harming yourself, please talk to someone you trust or a helpline today.", "herbs": [], "urgent": True}
    if GREET.search(msg) and len(msg.split()) <= 5:
        return {"reply": "Hello there! 👋🌿 I’m your Herbal Guide. Tell me what you’re feeling, like “I have a cough” or “my head hurts”, and I’ll suggest plants that are traditionally used. You can also ask about a plant, like tulsi or ginger. What’s bothering you today?", "herbs": []}
    if THANKS.search(msg):
        return {"reply": "You’re most welcome! 😊 Is there anything else I can help you with?", "herbs": []}
    if BYE.search(msg):
        return {"reply": "Take care, and stay healthy! 🌿👋", "herbs": []}
    if ABOUT.search(msg):
        return {"reply": "I’m a herbal guide! 🌿 Tell me a symptom (cough, headache, poor sleep, acidity, acne...) and I’ll suggest traditional herbs, how people take them, and what to be careful about. I can’t diagnose or replace a doctor.", "herbs": []}

    _, matched = retriever.analyze(msg)
    hits = retriever.search(msg, top_k=3)
    if not hits:
        return {"reply": "Hmm, I couldn’t find a plant for that. 🤔 Could you describe it a different way? For example “cough”, “headache”, “can’t sleep”, “acidity” or “acne”. For anything serious, please see a doctor.", "herbs": []}

    def name_words(h):
        return re.findall(r"[a-z]+", h["herb"]["name"].lower())

    by_name = [h for h in hits if any(w in name_words(h) for w in matched)]
    if by_name:
        h = by_name[0]["herb"]
        return {"reply": f"Great choice! 🌱 Here’s what I know about {h['name']}:", "herbs": [h],
                "closing": "Always check with a doctor before using it, especially if you’re pregnant or take medicines. 🌿"}
    sw = [w for w in matched if w in retriever.symptom_vocab]
    topic = " ".join(sw[:3]) if sw else "that"
    return {"reply": random.choice(OPENERS).format(t=topic) + " Here are plants people traditionally use:",
            "herbs": [h["herb"] for h in hits], "closing": random.choice(CLOSERS)}


@app.post("/chat")
def chat(body: Chat):
    return reply(body.message)


@app.get("/")
def home():
    return FileResponse("static/index.html")