# app.py - Version mockée (données en mémoire)
import os

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()
# ============================================
# Connexion DB
# ============================================

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

# ============================================
#  ROUTES
# ============================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/questions/random', methods=['GET'])
def get_random_question():
    """Renvoie une question aléatoire avec ses stats de vote."""
    conn = get_db()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT q.id, q.option_a, q.option_b,
                       SUM(CASE WHEN v.choice = 'A' THEN 1 ELSE 0 END) AS votes_a,
                       SUM(CASE WHEN v.choice = 'B' THEN 1 ELSE 0 END) AS votes_b
                FROM questions q
                LEFT JOIN votes v ON q.id = v.question_id
                GROUP BY q.id, q.option_a, q.option_b
                ORDER BY RAND()
                LIMIT 1
            """)
            question = cur.fetchone()
            if not question:
                return jsonify({'error': 'No questions found'}), 404

            # MySQL renvoie des Decimal pour les SUM, on convertit en int
            question['votes_a'] = int(question['votes_a'] or 0)
            question['votes_b'] = int(question['votes_b'] or 0)
            return jsonify(question)
    finally:
        conn.close()


@app.route('/api/questions', methods=['GET'])
def list_questions():
    """Liste toutes les questions avec leurs stats."""
    conn = get_db()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT q.id, q.option_a, q.option_b, q.created_at,
                       SUM(CASE WHEN v.choice = 'A' THEN 1 ELSE 0 END) AS votes_a,
                       SUM(CASE WHEN v.choice = 'B' THEN 1 ELSE 0 END) AS votes_b
                FROM questions q
                LEFT JOIN votes v ON q.id = v.question_id
                GROUP BY q.id, q.option_a, q.option_b, q.created_at
                ORDER BY q.created_at DESC
            """)
            questions = cur.fetchall()
            for q in questions:
                q['votes_a'] = int(q['votes_a'] or 0)
                q['votes_b'] = int(q['votes_b'] or 0)
            return jsonify(questions)
    finally:
        conn.close()


@app.route('/api/questions', methods=['POST'])
def create_question():
    """Crée une nouvelle question."""
    data = request.get_json()
    if not data or 'option_a' not in data or 'option_b' not in data:
        return jsonify({'error': 'option_a and option_b required'}), 400

    option_a = data['option_a'].strip()
    option_b = data['option_b'].strip()

    if not option_a or not option_b:
        return jsonify({'error': 'options cannot be empty'}), 400

    conn = get_db()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "INSERT INTO questions (option_a, option_b) VALUES (%s, %s)",
                (option_a, option_b)
            )
            conn.commit()
            new_id = cur.lastrowid

            cur.execute("""
                SELECT id, option_a, option_b, created_at
                FROM questions
                WHERE id = %s
            """, (new_id,))
            return jsonify(cur.fetchone()), 201
    finally:
        conn.close()


@app.route('/api/questions/<int:question_id>/vote', methods=['POST'])
def vote(question_id):
    """Enregistre un vote pour une question (choice = 'A' ou 'B')."""
    data = request.get_json()
    if not data or data.get('choice') not in ('A', 'B'):
        return jsonify({'error': "choice must be 'A' or 'B'"}), 400

    conn = get_db()
    try:
        with conn.cursor(dictionary=True) as cur:
            # Vérifier que la question existe
            cur.execute("SELECT id FROM questions WHERE id = %s", (question_id,))
            if not cur.fetchone():
                return jsonify({'error': 'Question not found'}), 404

            # Enregistrer le vote
            cur.execute(
                "INSERT INTO votes (question_id, choice) VALUES (%s, %s)",
                (question_id, data['choice'])
            )
            conn.commit()

            # Renvoyer les stats à jour pour que le front les affiche immédiatement
            cur.execute("""
                SELECT q.id, q.option_a, q.option_b,
                       SUM(CASE WHEN v.choice = 'A' THEN 1 ELSE 0 END) AS votes_a,
                       SUM(CASE WHEN v.choice = 'B' THEN 1 ELSE 0 END) AS votes_b
                FROM questions q
                LEFT JOIN votes v ON q.id = v.question_id
                WHERE q.id = %s
                GROUP BY q.id, q.option_a, q.option_b
            """, (question_id,))
            result = cur.fetchone()
            result['votes_a'] = int(result['votes_a'] or 0)
            result['votes_b'] = int(result['votes_b'] or 0)
            return jsonify(result), 201
    finally:
        conn.close()


@app.route('/api/questions/<int:question_id>/stats', methods=['GET'])
def get_stats(question_id):
    """Renvoie les stats détaillées d'une question."""
    conn = get_db()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT q.id, q.option_a, q.option_b,
                       SUM(CASE WHEN v.choice = 'A' THEN 1 ELSE 0 END) AS votes_a,
                       SUM(CASE WHEN v.choice = 'B' THEN 1 ELSE 0 END) AS votes_b,
                       COUNT(v.id) AS total_votes
                FROM questions q
                LEFT JOIN votes v ON q.id = v.question_id
                WHERE q.id = %s
                GROUP BY q.id, q.option_a, q.option_b
            """, (question_id,))
            result = cur.fetchone()
            if not result:
                return jsonify({'error': 'Question not found'}), 404

            result['votes_a'] = int(result['votes_a'] or 0)
            result['votes_b'] = int(result['votes_b'] or 0)
            result['total_votes'] = int(result['total_votes'] or 0)
            return jsonify(result)
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)