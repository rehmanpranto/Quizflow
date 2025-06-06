from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from flask_mail import Mail, Message

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# --- Mail Configuration ---
# Configure Flask-Mail with credentials from your .env file
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Embedded quiz data
QUIZ_DATA = {
    "title": "Market Research and Marketing Mix Quiz",
    "timeLimit": 1800,  # 30 minutes in seconds
    "questions": [
        {
            "id": 1,
            "question": "What is the primary purpose of market research?",
            "options": [
                "To increase sales immediately",
                "To understand customer needs and market trends",
                "To reduce business costs",
                "To hire more employees"
            ],
            "correct_answer": 1
        },
        {
            "id": 2,
            "question": "Which of the following is NOT part of the traditional marketing mix (4Ps)?",
            "options": [
                "Product",
                "Price",
                "People",
                "Promotion"
            ],
            "correct_answer": 2
        },
        {
            "id": 3,
            "question": "What does 'segmentation' mean in marketing?",
            "options": [
                "Dividing the market into distinct groups",
                "Combining all customers into one group",
                "Setting prices for products",
                "Creating advertisements"
            ],
            "correct_answer": 0
        },
        {
            "id": 4,
            "question": "Which research method involves collecting data from a large number of respondents?",
            "options": [
                "Focus groups",
                "In-depth interviews",
                "Surveys",
                "Observation"
            ],
            "correct_answer": 2
        },
        {
            "id": 5,
            "question": "What is the 'Place' element in the marketing mix?",
            "options": [
                "The physical location of the company",
                "Distribution channels and locations where products are sold",
                "The price of the product",
                "The promotion strategy"
            ],
            "correct_answer": 1
        }
    ]
}

# In-memory storage for submissions (replaces database)
user_submissions = {}
user_accounts = {}

# --- Routes ---
@app.route('/')
def index_page():
    return send_from_directory('.', 'index.html')

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    print(f"DEBUG: Received registration data: {data}")
    
    name = data.get('name') if data else None
    email = data.get('email') if data else None
    password = data.get('password') if data else None

    if not data or not name or not email or not password:
        return jsonify({"success": False, "message": "All fields (name, email, password) are required"}), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"success": False, "message": "Invalid email format"}), 400
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long"}), 400

    if email in user_accounts:
        return jsonify({"success": False, "message": "Email already registered"}), 409
    
    user_accounts[email] = {
        "name": name,
        "email": email,
        "password": password,  # In production, this should be hashed
        "created_at": datetime.now(timezone.utc)
    }
    
    return jsonify({
        "success": True, 
        "message": "User registered successfully",
        "user_id": email  # Using email as user ID for simplicity
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    print(f"DEBUG: Received login data: {data}")
    email = data.get('email') if data else None
    password = data.get('password') if data else None

    if not data or not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    
    if email not in user_accounts:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401
    
    if user_accounts[email]["password"] != password:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401
    
    # Check if user has already taken the quiz
    if email in user_submissions:
        submission = user_submissions[email]
        return jsonify({
            "success": True, 
            "quiz_already_taken": True,
            "message": f"You have already completed '{QUIZ_DATA['title']}'. Here are your previous results.",
            "email": email, 
            "user_id": email,
            "past_results": { 
                "submission_id": submission["submission_id"],
                "quizTitle": QUIZ_DATA["title"],
                "score": submission["score"],
                "totalQuestions": submission["total_questions"],
                "percentage": submission["percentage"], 
                "feedback": submission["feedback"]
            }
        }), 200
    else:
        return jsonify({"success": True, "message": "Login successful. You can start the quiz.", "email": email, "user_id": email}), 200

@app.route('/api/quiz', methods=['GET'])
def get_quiz():
    try:
        return jsonify({
            "success": True,
            "title": QUIZ_DATA["title"],
            "timeLimit": QUIZ_DATA["timeLimit"],
            "questions": [
                {
                    "id": q["id"],
                    "question": q["question"],
                    "options": q["options"]
                } for q in QUIZ_DATA["questions"]
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred while fetching the quiz."}), 500

@app.route('/api/submit', methods=['POST'])
def submit_quiz():
    data = request.get_json()
    user_email = data.get('email') if data else None
    user_answers_indices = data.get('answers', []) if data else []

    if not data or not user_email or not isinstance(user_answers_indices, list):
        return jsonify({"success": False, "message": "User email and answers list are required."}), 400

    try:
        if user_email not in user_accounts:
            return jsonify({"success": False, "message": "User not found."}), 401

        if user_email in user_submissions:
            return jsonify({"success": False, "message": "This quiz has already been submitted by you."}), 403

        score = 0
        total_questions = len(QUIZ_DATA["questions"])
        detailed_results_for_frontend = []

        for i, question in enumerate(QUIZ_DATA["questions"]):
            correct_answer_index = question["correct_answer"]
            user_selected_index = None
            user_selected_text = "Not Answered"
            is_correct_flag = False

            if i < len(user_answers_indices) and user_answers_indices[i] is not None:
                try:
                    user_selected_index = int(user_answers_indices[i])
                    if 0 <= user_selected_index < len(question["options"]):
                        user_selected_text = question["options"][user_selected_index]
                    else:
                        user_selected_index = None 
                        user_selected_text = "Invalid Option Selected"
                except (ValueError, TypeError):
                    user_selected_index = None 
                    user_selected_text = "Invalid Answer Format"
            
            if user_selected_index == correct_answer_index:
                score += 1
                is_correct_flag = True
            
            detailed_results_for_frontend.append({
                "id": question["id"],
                "question": question["question"],
                "your_answer": user_selected_text,
                "correct_answer": question["options"][correct_answer_index],
                "is_correct": is_correct_flag
            })

        percentage = (score / total_questions) * 100 if total_questions > 0 else 0
        feedback_name = user_email.split('@')[0]
        feedback_text = "" 
        if percentage == 100: feedback_text = f"Perfect score, {feedback_name}! You're a whiz!"
        elif percentage >= 80: feedback_text = f"Excellent work, {feedback_name}!"
        elif percentage >= 60: feedback_text = f"Good job, {feedback_name}!"
        elif percentage >= 40: feedback_text = f"Not bad, {feedback_name}. Keep practicing!"
        else: feedback_text = f"Keep learning, {feedback_name}!"

        submission_id = f"sub_{user_email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        user_submissions[user_email] = {
            "submission_id": submission_id,
            "score": score,
            "total_questions": total_questions,
            "percentage": percentage,
            "feedback": feedback_text,
            "submitted_at": datetime.now(timezone.utc),
            "detailed_results": detailed_results_for_frontend
        }

        print(f"Quiz submitted by: {user_email}, Score: {score}/{total_questions}, Submission ID: {submission_id}")

        # --- Send Email Notification to Admin ---
        admin_email = os.getenv('ADMIN_EMAIL_RECIPIENT')
        if admin_email:
            try:
                quiz_title = QUIZ_DATA.get("title", "Quiz")
                subject = f"Quiz Submission: {user_email} on '{quiz_title}'"
                body = f"""
                A user has just completed a quiz.

                User Email: {user_email}
                Quiz Title: {quiz_title}
                Score: {score} out of {total_questions}
                Percentage: {percentage:.2f}%
                Feedback: {feedback_text}

                Submitted at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
                """
                msg = Message(subject, recipients=[admin_email], body=body)
                mail.send(msg)
                print(f"Successfully sent submission email to admin: {admin_email}")
            except Exception as e:
                print(f"!!! FAILED to send submission email to admin: {e}")
        else:
            print("!!! ADMIN_EMAIL_RECIPIENT not set in .env. Skipping email notification.")


        return jsonify({
            "success": True, "email": user_email, "submission_id": submission_id,
            "score": score, "totalQuestions": total_questions, "percentage": percentage,
            "feedback": feedback_text, "detailed_results": detailed_results_for_frontend
        }), 200

    except Exception as e:
        print(f"Error during quiz submission: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred during submission."}), 500

@app.route('/api/user/submissions', methods=['GET'])
def get_user_submissions():
    user_email = request.args.get('email')
    if not user_email:
        return jsonify({"success": False, "message": "User email parameter is required."}), 400
    
    try:
        if user_email not in user_accounts:
            return jsonify({"success": False, "message": "User not found."}), 404

        submissions_list = []
        if user_email in user_submissions:
            submission = user_submissions[user_email]
            submissions_list.append({
                "submission_id": submission["submission_id"],
                "quiz_id": "default_quiz",
                "quiz_title": QUIZ_DATA["title"],
                "score": submission["score"],
                "total_questions_in_quiz": submission["total_questions"],
                "percentage": submission["percentage"],
                "submitted_at": submission["submitted_at"].isoformat()
            })
            
        return jsonify({"success": True, "submissions": submissions_list})
    except Exception as e:
        print(f"Error fetching user submissions: {e}")
        return jsonify({"success": False, "message": "An error occurred while fetching submissions."}), 500

@app.route('/api/submission/<submission_id_str>/details', methods=['GET'])
def get_submission_details(submission_id_str):
    try:
        # Find submission by ID
        user_email = None
        submission = None
        
        for email, sub in user_submissions.items():
            if sub["submission_id"] == submission_id_str:
                user_email = email
                submission = sub
                break
        
        if not submission:
            return jsonify({"success": False, "message": "Submission not found."}), 404

        summary_response = {
            "submission_id": submission["submission_id"],
            "quiz_id": "default_quiz",
            "quiz_title": QUIZ_DATA["title"],
            "score": submission["score"],
            "total_questions_in_quiz": submission["total_questions"],
            "percentage": submission["percentage"],
            "feedback_text": submission["feedback"],
            "submitted_at": submission["submitted_at"].isoformat(),
            "user_email": user_email
        }

        # Convert detailed results to match frontend expectations
        detailed_questions_list = []
        for result in submission["detailed_results"]:
            detailed_questions_list.append({
                "question_id": str(result["id"]),
                "question_text": result["question"],
                "user_selected_answer_text": result["your_answer"],
                "correct_answer_text": result["correct_answer"],
                "is_correct": result["is_correct"]
            })
            
        return jsonify({"success": True, "summary": summary_response, "details": detailed_questions_list})

    except Exception as e:
        print(f"Error fetching submission details for {submission_id_str}: {e}")
        return jsonify({"success": False, "message": "An error occurred while fetching submission details."}), 500

# --- End of Routes ---

if __name__ == '__main__':
    print("Starting Quizflow application with embedded data...")
    print(f"Quiz: {QUIZ_DATA['title']} ({len(QUIZ_DATA['questions'])} questions)")
    app.run(debug=True, port=5001)