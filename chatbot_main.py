from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from sentence_transformers import SentenceTransformer

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- SCHEMA ----------------
class UserInput(BaseModel):
    text: str

# ---------------- DB CONNECTION ----------------
conn = psycopg2.connect(
    dbname="ayurveda_chatbot",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5433"
)

# ---------------- LOAD MODEL ----------------
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.get("/")
def home():
    return {"message": "Ayurvedic Chatbot Running"}

# ---------------- NLP ----------------
def extract_info(text):
    text = text.lower()
    symptoms = []
    ritu = None

    if "acidity" in text:
        symptoms.append("acidity")
    if "heat" in text or "burning" in text:
        symptoms.append("heat")
    if "dryness" in text:
        symptoms.append("dryness")

    if "summer" in text:
        ritu = "grishma"
    elif "rain" in text:
        ritu = "varsha"
    elif "winter" in text:
        ritu = "hemanta"

    return symptoms, ritu

# ---------------- VECTOR SEARCH ----------------
def get_similar_symptoms(text):
    embedding = model.encode(text).tolist()
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    cur = conn.cursor()
    cur.execute("""
        SELECT symptom
        FROM symptom_embeddings
        ORDER BY embedding <-> %s::vector
        LIMIT 3
    """, (embedding_str,))

    results = cur.fetchall()
    cur.close()
    return [r[0] for r in results]

# ---------------- DOSHA ----------------
def get_dosha(symptoms):
    cur = conn.cursor()
    cur.execute("""
        SELECT LOWER(dosha), COUNT(*) as score
        FROM symptoms_map
        WHERE LOWER(symptom) = ANY(%s)
        GROUP BY LOWER(dosha)
        ORDER BY score DESC
        LIMIT 1
    """, (symptoms,))
    result = cur.fetchone()
    cur.close()
    return result[0] if result else None

# ---------------- DIET ----------------
def get_diet(dosha, ritu):
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT food, type
        FROM diet_recommendations
        WHERE LOWER(dosha) = %s AND LOWER(ritu) = %s
    """, (dosha, ritu))
    result = cur.fetchall()
    cur.close()
    return result

# ---------------- MAIN API ----------------
@app.post("/recommend")
def recommend(user: UserInput):

    # Step 1: Extract
    symptoms, ritu = extract_info(user.text)

    # Step 2: Semantic matching
    similar = get_similar_symptoms(user.text)
    symptoms.extend(similar)
    symptoms = list(set([s.lower() for s in symptoms]))  # normalize + remove duplicates

    # Step 3: Get dosha
    dosha = get_dosha(symptoms)
    if not dosha:
        return {"error": "Dosha not found"}

    # Step 4: Default ritu
    if not ritu:
        ritu = "grishma"
    ritu = ritu.lower()

    # Step 5: Get diet
    diet = get_diet(dosha, ritu)

    recommended = list(set([d[0] for d in diet if d[1] == 'recommended']))
    avoid = list(set([d[0] for d in diet if d[1] == 'avoid']))

    return {
        "detected_symptoms": symptoms,
        "ritu": ritu,
        "dosha": dosha,
        "recommended_food": recommended,
        "avoid_food": avoid
    }