import os
from datetime import datetime
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ============================================
# Configuration de l'ORM
# ============================================
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============================================
# Modèles de données
# ============================================
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    votes = db.relationship('Vote', backref='question', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        votes_a = sum(1 for v in self.votes if v.choice == 'A')
        votes_b = sum(1 for v in self.votes if v.choice == 'B')
        return {
            'id': self.id,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'votes_a': votes_a,
            'votes_b': votes_b,
            'total_votes': votes_a + votes_b
        }

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    choice = db.Column(db.String(1), nullable=False) # 'A' ou 'B'

# ============================================
# Initialisation de la base au démarrage
# ============================================
with app.app_context():
    # Crée les tables uniquement si elles n'existent pas encore
    db.create_all()

    if Question.query.count() == 0:
        # La base de données est vide. Injection des fixtures
        
        fixtures = [
            Question(option_a="Pain au chocolat", option_b="Chocolatine"),
            Question(option_a="Être invisible", option_b="Pouvoir voler")
        ]
        
        db.session.bulk_save_objects(fixtures)
        db.session.commit()

# ============================================
# ROUTES
# ============================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/questions/random', methods=['GET'])
def get_random_question():
    """Renvoie une question aléatoire avec ses stats de vote."""
    # Sélectionne une ligne de manière aléatoire via l'ORM
    question = Question.query.order_by(func.rand()).first()
    if not question:
        return jsonify({'error': 'No questions found'}), 404
    return jsonify(question.to_dict())

@app.route('/api/questions', methods=['GET'])
def list_questions():
    """Liste toutes les questions avec leurs stats."""
    questions = Question.query.order_by(Question.created_at.desc()).all()
    return jsonify([q.to_dict() for q in questions])

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

    new_question = Question(option_a=option_a, option_b=option_b)
    db.session.add(new_question)
    db.session.commit()
    
    return jsonify(new_question.to_dict()), 201

@app.route('/api/questions/<int:question_id>/vote', methods=['POST'])
def vote(question_id):
    """Enregistre un vote pour une question (choice = 'A' ou 'B')."""
    data = request.get_json()
    if not data or data.get('choice') not in ('A', 'B'):
        return jsonify({'error': "choice must be 'A' or 'B'"}), 400

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    new_vote = Vote(question_id=question_id, choice=data['choice'])
    db.session.add(new_vote)
    db.session.commit()

    return jsonify(question.to_dict()), 201

@app.route('/api/questions/<int:question_id>/stats', methods=['GET'])
def get_stats(question_id):
    """Renvoie les stats détaillées d'une question."""
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    return jsonify(question.to_dict())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)