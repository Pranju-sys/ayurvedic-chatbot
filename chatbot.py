from sentence_transformers import SentenceTransformer
import psycopg2

model = SentenceTransformer('all-MiniLM-L6-v2')

conn = psycopg2.connect(
    dbname="ayurveda_chatbot",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5433"
)

cur = conn.cursor()

cur.execute("SELECT symptom FROM symptoms_map")
rows = cur.fetchall()

for row in rows:
    symptom = row[0]
    embedding = model.encode(symptom).tolist()

    cur.execute("""
        INSERT INTO symptom_embeddings (symptom, embedding)
        VALUES (%s, %s)
    """, (symptom, embedding))

conn.commit()
cur.close()
conn.close()
