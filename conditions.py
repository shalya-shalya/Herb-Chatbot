import re

# keywords -> simple home tips + when to see a doctor
CONDITIONS = [
    {"name": "stomach pain", "words": r"stomach|tummy|belly|abdomen|abdominal|gastric",
     "tips": ["Sip warm water slowly through the day.", "Try jeera (cumin) water or ajwain water, warm.", "Eat light, small meals (rice, banana, curd). Avoid oily, spicy food and cold drinks."],
     "doctor": "See a doctor if the pain is severe or lasts more than 1 to 2 days, or comes with vomiting, fever, blood in stool, black stool, or a hard swollen belly. Pain on the lower right side needs urgent care."},
    {"name": "cold", "words": r"\bcold\b|runny nose|blocked nose|sneez|stuffy",
     "tips": ["Drink warm fluids and rest well.", "Steam inhalation 1 to 2 times a day can open a blocked nose.", "Gargle with warm salt water if the throat is sore."],
     "doctor": "See a doctor if it lasts more than 7 to 10 days, you have a high fever, trouble breathing, or severe ear or sinus pain."},
    {"name": "cough", "words": r"cough|cof\b|phlegm|mucus",
     "tips": ["Sip warm water or tea often.", "Honey in warm water soothes a dry cough (not for children under 1 year).", "Avoid smoke, dust and cold drinks."],
     "doctor": "See a doctor if the cough lasts more than 2 weeks, you cough up blood, have breathlessness, chest pain, or a high fever."},
    {"name": "sore throat", "words": r"sore throat|throat pain|throat ache|hoarse",
     "tips": ["Gargle with warm salt water 3 times a day.", "Sip warm tea with ginger or tulsi.", "Rest your voice."],
     "doctor": "See a doctor if you cannot swallow, have a high fever, white patches in the throat, or it lasts more than a week."},
    {"name": "headache", "words": r"headache|head ache|head pain|head hurts|my head|migraine",
     "tips": ["Drink water. Dehydration is a common cause.", "Rest in a quiet, dim room.", "Gently massage temples. Check your sleep and screen time."],
     "doctor": "See a doctor urgently for a sudden severe headache, or one with fever, stiff neck, confusion, weakness, or vision changes. Also see one if headaches keep coming back."},
    {"name": "fever", "words": r"fever|temperature|feverish",
     "tips": ["Rest and drink plenty of fluids.", "Wear light clothing and keep the room comfortable.", "Check your temperature every few hours."],
     "doctor": "See a doctor if fever is above 102°F (39°C), lasts more than 2 to 3 days, or comes with rash, severe headache, breathing trouble or confusion. Fever in babies needs a doctor right away."},
    {"name": "loose motions", "words": r"diarrh|loose motion|loose stool|watery stool",
     "tips": ["Drink ORS or plenty of fluids to avoid dehydration.", "Eat light food like rice, banana and curd.", "Wash hands well."],
     "doctor": "See a doctor if it lasts more than 2 days, or there is blood in stool, high fever, severe pain, or signs of dehydration (very dry mouth, little urine, dizziness). Children and the elderly need care sooner."},
    {"name": "constipation", "words": r"constipat|hard stool|not passing stool",
     "tips": ["Drink more water and eat more fiber (fruits, vegetables, whole grains).", "Warm water in the morning can help.", "A short daily walk helps your gut."],
     "doctor": "See a doctor if it lasts more than a week, or there is blood in stool, severe pain, or unexplained weight loss."},
    {"name": "acidity and gas", "words": r"acidity|heartburn|acid reflux|\bgas\b|bloat|indigestion|burp",
     "tips": ["Eat smaller meals and don't lie down right after eating.", "Avoid very spicy, oily food, tea on an empty stomach, and late dinners.", "Cold milk or buttermilk can help some people."],
     "doctor": "See a doctor if it happens often, you have trouble swallowing, vomiting, black stool, weight loss, or chest pain."},
    {"name": "nausea", "words": r"nausea|vomit|motion sickness|queasy",
     "tips": ["Sip small amounts of water or ORS.", "Fresh air helps. Eat dry, light food like crackers.", "Ginger tea is a common help."],
     "doctor": "See a doctor if vomiting lasts more than a day, you cannot keep fluids down, or there is severe pain or blood."},
    {"name": "poor sleep", "words": r"sleep|insomnia|cannot sleep|can.?t sleep",
     "tips": ["Keep a fixed sleep time and avoid screens an hour before bed.", "Avoid tea, coffee and heavy meals late in the day.", "Warm milk or a warm bath can relax you."],
     "doctor": "See a doctor if poor sleep lasts more than 2 to 3 weeks or affects your work and mood."},
    {"name": "stress and anxiety", "words": r"stress|anxiety|anxious|tension|worried|nervous|panic",
     "tips": ["Try slow breathing: in for 4, out for 6, for a few minutes.", "Take short walks and keep a steady routine.", "Talk to someone you trust."],
     "doctor": "Please talk to a doctor or counsellor if stress is affecting your daily life, sleep or appetite, or if you feel hopeless."},
    {"name": "high blood sugar", "words": r"blood sugar|diabetes|diabetic|sugar level",
     "tips": ["Cut down sweets and sugary drinks, and walk after meals.", "Eat more fiber and vegetables.", "Check your sugar regularly if you have diabetes."],
     "doctor": "Do not replace diabetes medicines with herbs. See your doctor regularly, and check with them before adding any herb, because some can drop sugar too low."},
    {"name": "toothache", "words": r"tooth|teeth|gum pain|dental",
     "tips": ["Rinse with warm salt water.", "Floss gently to remove stuck food.", "Avoid very hot, cold or sweet things."],
     "doctor": "See a dentist soon. A toothache usually means a problem that needs treatment, especially with swelling, fever or pus."},
    {"name": "skin problems", "words": r"acne|pimple|skin|rash|itch|dandruff",
     "tips": ["Wash the face gently twice a day. Don't squeeze pimples.", "Do a patch test before putting any plant paste on your skin.", "Drink water and keep hair and pillows clean."],
     "doctor": "See a doctor if the rash spreads, hurts, has pus, or lasts more than 2 weeks, or if there is facial swelling or breathing trouble."},
    {"name": "hair fall", "words": r"hair fall|hairfall|hair loss|grey hair|dandruff",
     "tips": ["Eat enough protein, iron and vitamins.", "Oil gently and avoid harsh heat styling.", "Manage stress and sleep well."],
     "doctor": "See a doctor if hair loss is sudden, in patches, or very heavy, since thyroid, iron or other issues can cause it."},
    {"name": "period cramps", "words": r"period|menstrual|menstruation|pms",
     "tips": ["A warm compress on the lower belly helps.", "Warm drinks like ginger or fennel tea may ease cramps.", "Light exercise and rest help."],
     "doctor": "See a doctor if pain is severe, periods are very heavy or irregular, or you may be pregnant."},
    {"name": "joint pain", "words": r"joint|arthritis|knee pain|body ache|body pain|back pain",
     "tips": ["Gentle movement and stretching help stiff joints.", "A warm compress eases stiffness.", "Turmeric milk is a common home choice."],
     "doctor": "See a doctor if there is swelling, redness, severe pain, or it lasts more than a couple of weeks."},
]

BEST = {
    "stomach pain": ["Ajwain", "Cumin", "Fennel"], "cold": ["Tulsi", "Ginger", "Black Pepper"],
    "cough": ["Mulethi", "Tulsi", "Ginger"], "sore throat": ["Mulethi", "Tulsi", "Clove"],
    "headache": ["Peppermint", "Lavender", "Ginger"], "fever": ["Tulsi", "Giloy", "Lemongrass"],
    "loose motions": ["Bael", "Jamun", "Isabgol"], "constipation": ["Triphala", "Isabgol", "Bael"],
    "acidity and gas": ["Cumin", "Fennel", "Aloe"], "nausea": ["Ginger", "Peppermint", "Coriander"],
    "poor sleep": ["Chamomile", "Ashwagandha", "Lavender"], "stress and anxiety": ["Ashwagandha", "Brahmi", "Tulsi"],
    "high blood sugar": ["Bitter Gourd", "Jamun", "Fenugreek"], "toothache": ["Clove"],
    "skin problems": ["Neem", "Aloe", "Turmeric"], "hair fall": ["Curry", "Amla", "Fenugreek"],
    "period cramps": ["Ginger", "Fennel", "Shatavari"], "joint pain": ["Turmeric", "Ginger"],
}

for c in CONDITIONS:
    c["rx"] = re.compile(c["words"], re.I)
    c["best"] = BEST.get(c["name"], [])


def find_conditions(text, limit=2):
    return [c for c in CONDITIONS if c["rx"].search(text)][:limit]