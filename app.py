from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import os
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy
import sqlitecloud # Import sqlitecloud
# from datetime import datetime # Optional: if you add a submitted_at timestamp

app = Flask(__name__, static_folder='.', static_url_path='') # [cite: 1]
CORS(app) # [cite: 1]

# --- Database Configuration ---
# Your provided SQLite Cloud connection string
# For production, consider moving the API key to an environment variable
DATABASE_URI = os.environ.get('DATABASE_URL', "sqlitecloud://cet6ewpbnk.g3.sqlite.cloud:8860/chinook.sqlite?apikey=utcIe4OyiZWo7s93AbaaRrflOnlYCToQgkvCMPaHBIk")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Optional: to suppress a warning

db = SQLAlchemy(app) # Initialize SQLAlchemy with the app

# --- Email Configuration ---
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com') # [cite: 1]
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587)) # [cite: 1]
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't'] # [cite: 1]
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't'] # [cite: 1]
# These are now treated as potentially usable defaults if not overridden by environment variables.
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'rehmanpranto@gmail.com') # [cite: 1]
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'hezp aujt tcxt ezol') # [cite: 1]
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME']) # [cite: 1]

mail = Mail(app) # [cite: 1]

# --- Database Models (Define your tables) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Relationship to QuizSubmission (optional, but good for ORM features)
    quiz_submissions = db.relationship('QuizSubmission', backref='submitter', lazy=True) # Changed backref to avoid conflict with User model

    def __repr__(self):
        return f'<User {self.email}>'

class QuizSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), db.ForeignKey('user.email'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    # submitted_at = db.Column(db.DateTime, default=datetime.utcnow) # Optional timestamp

    def __repr__(self):
        return f'<QuizSubmission {self.user_email} - Score: {self.score}>'

# --- Quiz Content (remains the same from your original file) ---
quiz_content = {
    "title": "Market Research and Marketing Mix Quiz", # [cite: 1]
    "timeLimit": 1200, # [cite: 1]
    "questions": [ # [cite: 1]
        {
            "id": 1, # [cite: 1]
            "question": "What is the primary purpose of market research?", # [cite: 1]
            "options": [ # [cite: 1]
                "To increase company profits immediately", # [cite: 1]
                "To gather, analyze, and interpret data about markets to inform business decisions", # [cite: 1]
                "To create advertising campaigns", # [cite: 1]
                "To hire new employees" # [cite: 1]
            ],
            "answer": 1 # [cite: 1]
        },
        {
            "id": 2, # [cite: 1]
            "question": "Which of the following is an example of primary research?", # [cite: 1]
            "options": [ # [cite: 1]
                "Reading industry reports", # [cite: 1]
                "Analyzing government statistics", # [cite: 1]
                "Conducting surveys with customers", # [cite: 1]
                "Reviewing competitor websites" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 3, # [cite: 1]
            "question": "What type of research involves analyzing existing data from reports and online sources?", # [cite: 1]
            "options": [ # [cite: 1]
                "Primary research", # [cite: 1]
                "Secondary research", # [cite: 1]
                "Qualitative research", # [cite: 1]
                "Quantitative research" # [cite: 1]
            ],
            "answer": 1 # [cite: 1]
        },
        {
            "id": 4, # [cite: 1]
            "question": "Which research method focuses on numerical data and closed-ended questions?", # [cite: 1]
            "options": [ # [cite: 1]
                "Qualitative research", # [cite: 1]
                "Observational research", # [cite: 1]
                "Quantitative research", # [cite: 1]
                "Focus group research" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 5, # [cite: 1]
            "question": "What are the 4Ps of marketing collectively known as?", # [cite: 1]
            "options": [ # [cite: 1]
                "Marketing strategy", # [cite: 1]
                "Marketing mix", # [cite: 1]
                "Marketing plan", # [cite: 1]
                "Marketing framework" # [cite: 1]
            ],
            "answer": 1 # [cite: 1]
        },
        {
            "id": 6, # [cite: 1]
            "question": "Which of the following is NOT one of the 4Ps of marketing?", # [cite: 1]
            "options": [ # [cite: 1]
                "Product", # [cite: 1]
                "Price", # [cite: 1]
                "People", # [cite: 1]
                "Place" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 7, # [cite: 1]
            "question": "The \"Product\" element of the marketing mix includes all of the following EXCEPT:", # [cite: 1]
            "options": [ # [cite: 1]
                "Design and features", # [cite: 1]
                "Quality and branding", # [cite: 1]
                "Distribution channels", # [cite: 1]
                "Packaging and warranties" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 8, # [cite: 1]
            "question": "What factors should be considered when determining the \"Price\" element?", # [cite: 1]
            "options": [ # [cite: 1]
                "Production costs only", # [cite: 1]
                "Competitor pricing only", # [cite: 1]
                "Production costs, competitor pricing, perceived value, and profit margins", # [cite: 1]
                "Customer demographics only" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 9, # [cite: 1]
            "question": "The \"Place\" element of the marketing mix primarily focuses on:", # [cite: 1]
            "options": [ # [cite: 1]
                "Where advertisements are placed", # [cite: 1]
                "How and where customers can access the product", # [cite: 1]
                "The physical location of the company", # [cite: 1]
                "The price point of the product" # [cite: 1]
            ],
            "answer": 1 # [cite: 1]
        },
        {
            "id": 10, # [cite: 1]
            "question": "Which of the following best describes the \"Promotion\" element?", # [cite: 1]
            "options": [ # [cite: 1]
                "Price discounts and sales", # [cite: 1]
                "Product development activities", # [cite: 1]
                "Communication strategies to inform and persuade customers", # [cite: 1]
                "Distribution logistics" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 11, # [cite: 1]
            "question": "What is a key benefit of conducting market research?", # [cite: 1]
            "options": [ # [cite: 1]
                "Guaranteeing product success", # [cite: 1]
                "Eliminating all business risks", # [cite: 1]
                "Understanding consumer needs and behaviors", # [cite: 1]
                "Reducing production costs" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 12, # [cite: 1]
            "question": "Which research method would be best for gathering detailed, non-numerical insights?", # [cite: 1]
            "options": [ # [cite: 1]
                "Online surveys with multiple choice questions", # [cite: 1]
                "Statistical analysis of sales data", # [cite: 1]
                "Open-ended interviews", # [cite: 1]
                "Quantitative polling" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 13, # [cite: 1]
            "question": "What is one purpose of market research mentioned in the text?", # [cite: 1]
            "options": [ # [cite: 1]
                "To hire marketing staff", # [cite: 1]
                "To assess market size and potential", # [cite: 1]
                "To design company logos", # [cite: 1]
                "To choose office locations" # [cite: 1]
            ],
            "answer": 1 # [cite: 1]
        },
        {
            "id": 14, # [cite: 1]
            "question": "The 4Ps of marketing must be:", # [cite: 1]
            "options": [ # [cite: 1]
                "Considered independently", # [cite: 1]
                "Managed by different departments", # [cite: 1]
                "Considered cohesively for effective strategy", # [cite: 1]
                "Changed frequently" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 15, # [cite: 1]
            "question": "Which promotional tool is NOT mentioned in the text?", # [cite: 1]
            "options": [ # [cite: 1]
                "Advertising", # [cite: 1]
                "Public relations", # [cite: 1]
                "Telemarketing", # [cite: 1]
                "Social media marketing" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 16, # [cite: 1]
            "question": "An example of qualitative research would be:", # [cite: 1]
            "options": [ # [cite: 1]
                "A survey asking customers to rate satisfaction on a scale of 1-10", # [cite: 1]
                "Counting how many people visit a store daily", # [cite: 1]
                "Focus groups discussing product preferences", # [cite: 1]
                "Analyzing website traffic statistics" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 17, # [cite: 1]
            "question": "What does market research help businesses evaluate regarding competitors?", # [cite: 1]
            "options": [ # [cite: 1]
                "Their employee satisfaction", # [cite: 1]
                "Their strengths and weaknesses", # [cite: 1]
                "Their office locations", # [cite: 1]
                "Their hiring practices" # [cite: 1]
            ],
            "answer": 1 # [cite: 1]
        },
        {
            "id": 18, # [cite: 1]
            "question": "The \"Place\" element is also known as:", # [cite: 1]
            "options": [ # [cite: 1]
                "Promotion", # [cite: 1]
                "Distribution", # [cite: 1]
                "Positioning", # [cite: 1]
                "Pricing" # [cite: 1]
            ],
            "answer": 1 # [cite: 1]
        },
        {
            "id": 19, # [cite: 1]
            "question": "Which statement about the marketing mix is true?", # [cite: 1]
            "options": [ # [cite: 1]
                "Each element works independently", # [cite: 1]
                "Price is the most important element", # [cite: 1]
                "All four elements are interconnected", # [cite: 1]
                "Promotion should be the primary focus" # [cite: 1]
            ],
            "answer": 2 # [cite: 1]
        },
        {
            "id": 20, # [cite: 1]
            "question": "What is the ultimate goal of the promotion element?", # [cite: 1]
            "options": [ # [cite: 1]
                "To reduce production costs", # [cite: 1]
                "To build awareness, generate interest, and drive sales", # [cite: 1]
                "To improve product quality", # [cite: 1]
                "To expand distribution channels" # [cite: 1]
            ],
            "answer": 1 # [cite: 1]
        }
    ]
}

# --- Routes ---
@app.route('/')
def index_page(): # Renamed to avoid conflict with any 'index' variable if it exists
    return send_from_directory('.', 'index.html') # [cite: 1]

@app.route('/api/auth/register', methods=['POST']) # [cite: 1]
def register_user():
    data = request.get_json() # [cite: 1]
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400 # [cite: 1]
    email = data.get('email') # [cite: 1]
    password = data.get('password') # [cite: 1]

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400 # [cite: 1]
    if "@" not in email or "." not in email.split("@")[-1]: # [cite: 1]
        return jsonify({"success": False, "message": "Invalid email format"}), 400 # [cite: 1]
    if len(password) < 6: # [cite: 1]
        return jsonify({"success": False, "message": "Password must be at least 6 characters long"}), 400 # [cite: 1]

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"success": False, "message": "Email already registered"}), 409 # [cite: 1]

    hashed_password = generate_password_hash(password) # [cite: 1]
    new_user = User(email=email, password_hash=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
        print(f"New user registered: {email}") # [cite: 1]
        return jsonify({"success": True, "message": "Registration successful. Please login."}), 201 # [cite: 1]
    except Exception as e:
        db.session.rollback()
        print(f"Error during registration: {e}")
        # It's good practice to log the full error e for debugging
        return jsonify({"success": False, "message": "Registration failed due to a server error."}), 500

@app.route('/api/auth/login', methods=['POST']) # [cite: 1]
def login_user():
    data = request.get_json() # [cite: 1]
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400 # [cite: 1]
    email = data.get('email') # [cite: 1]
    password = data.get('password') # [cite: 1]

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400 # [cite: 1]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password): # [cite: 1]
        submission = QuizSubmission.query.filter_by(user_email=email).first()
        if submission:
            return jsonify({ # [cite: 1]
                "success": False, # [cite: 1]
                "quiz_already_taken": True, # [cite: 1]
                "message": "You have already completed this quiz. Multiple attempts are not allowed." # [cite: 1]
            }), 200 # [cite: 1]
        return jsonify({"success": True, "message": "Login successful", "email": email}), 200 # [cite: 1]
    else:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401 # [cite: 1]

@app.route('/api/quiz', methods=['GET']) # [cite: 1]
def get_quiz():
    questions_for_frontend = [] # [cite: 1]
    for q_idx, q in enumerate(quiz_content["questions"]): # [cite: 1]
        questions_for_frontend.append({ # [cite: 1]
            "id": q["id"], # [cite: 1]
            "question": q["question"], # [cite: 1]
            "options": q["options"] # [cite: 1]
        })
    return jsonify({ # [cite: 1]
        "title": quiz_content["title"], # [cite: 1]
        "timeLimit": quiz_content["timeLimit"], # [cite: 1]
        "questions": questions_for_frontend # [cite: 1]
    })

@app.route('/api/submit', methods=['POST']) # [cite: 1]
def submit_quiz():
    data = request.get_json() # [cite: 1]
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400 # [cite: 1]

    user_email = data.get('email') # [cite: 1]
    user_answers = data.get('answers', []) # [cite: 1]

    if not user_email:
        return jsonify({"success": False, "message": "User email not provided with submission."}), 400 # [cite: 1]

    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"success": False, "message": "Unauthorized user or user not found."}), 401 # [cite: 1]

    existing_submission = QuizSubmission.query.filter_by(user_email=user_email).first()
    if existing_submission:
        return jsonify({ # [cite: 1]
            "success": False, # [cite: 1]
            "message": "This quiz has already been submitted by you." # [cite: 1]
        }), 403 # [cite: 1]

    score = 0 # [cite: 1]
    total_questions = len(quiz_content["questions"]) # [cite: 1]
    for i, question_data in enumerate(quiz_content["questions"]): # [cite: 1]
        correct_answer_index = question_data["answer"] # [cite: 1]
        user_selected_index = None # [cite: 1]
        if i < len(user_answers) and user_answers[i] is not None: # [cite: 1]
            try:
                user_selected_index = int(user_answers[i]) # [cite: 1]
            except (ValueError, TypeError):
                user_selected_index = None # [cite: 1]
        if user_selected_index == correct_answer_index: # [cite: 1]
            score += 1 # [cite: 1]

    percentage = (score / total_questions) * 100 if total_questions > 0 else 0 # [cite: 1]

    new_submission = QuizSubmission(user_email=user_email,
                                    score=score,
                                    total_questions=total_questions,
                                    percentage=percentage)
    try:
        db.session.add(new_submission)
        db.session.commit()
        print(f"User {user_email} submission recorded. Score: {score}/{total_questions}") # [cite: 1]
    except Exception as e:
        db.session.rollback()
        print(f"Error saving quiz submission: {e}")
        return jsonify({"success": False, "message": "Failed to save quiz results due to a server error."}), 500

    feedback_name = user_email.split('@')[0] # [cite: 1]
    feedback = "" # [cite: 1]
    if percentage == 100: # [cite: 1]
        feedback = f"Perfect score, {feedback_name}! You're a market research whiz!" # [cite: 1]
    elif percentage >= 80: # [cite: 1]
        feedback = f"Excellent work, {feedback_name}! You have a strong understanding." # [cite: 1]
    elif percentage >= 60: # [cite: 1]
        feedback = f"Good job, {feedback_name}! You're getting the hang of it." # [cite: 1]
    elif percentage >= 40: # [cite: 1]
        feedback = f"Not bad, {feedback_name}. A little more study and you'll ace it!" # [cite: 1]
    else:
        feedback = f"Keep learning, {feedback_name}! Market research is a valuable skill." # [cite: 1]

    print(f"Quiz submitted by: {user_email}, Score: {score}/{total_questions}, Percentage: {percentage:.2f}%") # [cite: 1]

    admin_email_recipient = "rehmanpranto@gmail.com" # [cite: 1]
    email_recipients_list = [admin_email_recipient, user_email] # [cite: 1]
    email_subject = f"Quiz Results for {user_email} - {quiz_content['title']}" # [cite: 1]
    email_body_text = f"""
    Hello {feedback_name},

    Here are your results for the quiz: "{quiz_content['title']}".

    User Email: {user_email}
    Score: {score}/{total_questions}
    Percentage: {percentage:.2f}%
    Feedback: {feedback}

    This report was also sent to the site administrator.

    Thank you for participating!
    """ # [cite: 1]

    email_body_html = f"""
    <html><body>
    <p>Hello {feedback_name},</p>
    <p>Here are your results for the quiz: "<strong>{quiz_content['title']}</strong>".</p>
    <ul>
      <li><strong>User Email:</strong> {user_email}</li>
      <li><strong>Score:</strong> {score}/{total_questions}</li>
      <li><strong>Percentage:</strong> {percentage:.2f}%</li>
      <li><strong>Feedback:</strong> {feedback}</li>
    </ul>
    <p>This report was also sent to the site administrator.</p>
    <p>Thank you for participating!</p>
    </body></html>
    """ # [cite: 1]

    try:
        mail_user = app.config.get('MAIL_USERNAME') # [cite: 1]
        mail_pass = app.config.get('MAIL_PASSWORD') # [cite: 1]

        if not mail_user or not mail_pass or \
           mail_user == 'YOUR_SENDER_EMAIL@example.com' or \
           mail_pass == 'YOUR_GMAIL_APP_PASSWORD': # [cite: 1]
            warning_message = "WARNING: Email credentials are not properly configured. " # [cite: 1]
            if mail_user == 'YOUR_SENDER_EMAIL@example.com' or \
               mail_pass == 'YOUR_GMAIL_APP_PASSWORD': # [cite: 1]
                warning_message += "Default generic placeholders detected. " # [cite: 1]
            elif not mail_user or not mail_pass: # [cite: 1]
                warning_message += "MAIL_USERNAME or MAIL_PASSWORD is significantly missing. " # [cite: 1]
            warning_message += "Skipping email sending." # [cite: 1]
            print(warning_message) # [cite: 1]
            print(f"Current MAIL_USERNAME used for check: {mail_user}") # [cite: 1]
        else:
            msg = Message(subject=email_subject,
                          recipients=email_recipients_list,
                          body=email_body_text,
                          html=email_body_html,
                          sender=app.config['MAIL_DEFAULT_SENDER']) # [cite: 1]
            mail.send(msg) # [cite: 1]
            print(f"Report email sent successfully to {', '.join(email_recipients_list)}") # [cite: 1]
    except Exception as e:
        print(f"Error sending email: {e}") # [cite: 1]

    return jsonify({ # [cite: 1]
        "success": True, # [cite: 1]
        "email": user_email, # [cite: 1]
        "score": score, # [cite: 1]
        "totalQuestions": total_questions, # [cite: 1]
        "percentage": percentage, # [cite: 1]
        "feedback": feedback # [cite: 1]
    })

def create_tables():
    with app.app_context():
        print("Attempting to connect to database and create tables if they don't exist...")
        try:
            # Test connection (optional, but good for diagnostics with sqlitecloud)
            # For sqlitecloud, the driver itself will handle connection when SQLAlchemy interacts
            # A direct sqlitecloud.connect() call here is mainly for explicit testing
            # conn_test_uri = app.config['SQLALCHEMY_DATABASE_URI']
            # conn_test = sqlitecloud.connect(conn_test_uri)
            # print("Successfully connected to SQLite Cloud for table creation check (direct test).")
            # conn_test.close()

            db.create_all()
            print("Database tables checked/created successfully (if they didn't exist).")
        except Exception as e:
            print(f"Error during table creation or connection test: {e}")
            print("Please ensure your DATABASE_URI is correct, the SQLite Cloud service is reachable,")
            print("and the sqlitecloud-python driver is installed correctly.")

if __name__ == '__main__':
    create_tables() # Call this function to ensure tables are set up

    print(f"Attempting to use MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}") # [cite: 1]
    mail_user_startup = app.config.get('MAIL_USERNAME') # [cite: 1]
    mail_pass_startup = app.config.get('MAIL_PASSWORD') # [cite: 1]

    if not mail_user_startup or not mail_pass_startup or \
       mail_user_startup == 'YOUR_SENDER_EMAIL@example.com' or \
       mail_pass_startup == 'YOUR_GMAIL_APP_PASSWORD': # [cite: 1]
        print("\n*********************************************************************") # [cite: 1]
        print("WARNING: Email sending might be disabled or use default generic placeholders.") # [cite: 1]
        print("Please ensure MAIL_USERNAME and MAIL_PASSWORD are correctly set") # [cite: 1]
        print("(preferably as environment variables) for reliable email functionality.") # [cite: 1]
        if mail_user_startup == 'YOUR_SENDER_EMAIL@example.com' or \
           mail_pass_startup == 'YOUR_GMAIL_APP_PASSWORD': # [cite: 1]
            print("Default generic placeholder credentials detected.") # [cite: 1]
        elif not mail_user_startup or not mail_pass_startup: # [cite: 1]
            print("MAIL_USERNAME or MAIL_PASSWORD seems to be missing or empty.") # [cite: 1]
        print(f"Currently configured MAIL_USERNAME for startup check: {mail_user_startup}") # [cite: 1]
        print("*********************************************************************\n") # [cite: 1]
    else:
        print("Email credentials appear to be configured.") # [cite: 1]

    app.run(debug=True, port=5001) # [cite: 1]