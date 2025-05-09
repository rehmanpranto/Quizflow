from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS # For handling Cross-Origin Resource Sharing

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app) # Enable CORS for all routes. For production, restrict to your frontend's domain.

# --- Mock User Data (Simulating a User Database) ---
# Reverted to previous default credentials
# In a real application, passwords would be hashed and stored securely.
MOCK_USERS_BACKEND = {
    "student1": "pass123",
    "teacher": "admin456",
    "student01": "pass456",
    "user": "password" # A generic user for testing
}

# --- In-memory store for submitted quizzes ---
# This will reset when the server restarts. For persistence, use a database.
SUBMITTED_QUIZZES = set()


# --- Quiz Content ---
quiz_content = {
    "title": "Market Research Fundamentals Quiz",
    "timeLimit": 900, # 900 seconds (15 minutes)
    "questions": [
        {
            "id": 1,
            "question": "What does market research primarily involve?",
            "options": [
                "Only gathering data about customers",
                "Gathering, analyzing, and interpreting data about a market (customers, competitors, trends)",
                "Exclusively analyzing competitor strategies",
                "Interpreting market trends without data collection"
            ],
            "answer": 1
        },
        {
            "id": 2,
            "question": "What is the main goal of market research according to the passage?",
            "options": [
                "To create complex statistical models",
                "To publish academic studies",
                "To inform business decisions and develop effective strategies",
                "To solely track competitor pricing"
            ],
            "answer": 2
        },
        {
            "id": 3,
            "question": "Which type of research involves collecting original data?",
            "options": [
                "Secondary Research",
                "Quantitative Research",
                "Primary Research",
                "Qualitative Research"
            ],
            "answer": 2
        },
        {
            "id": 4,
            "question": "Surveys, interviews, focus groups, and observations are examples of methods used in which type of research?",
            "options": [
                "Secondary Research",
                "Primary Research",
                "Trend Analysis",
                "Competitor Analysis"
            ],
            "answer": 1
        },
        {
            "id": 5,
            "question": "What does Secondary Research involve?",
            "options": [
                "Conducting new interviews with customers",
                "Observing consumer behavior in stores",
                "Analyzing existing data from reports, studies, or online sources",
                "Creating original surveys for a specific product"
            ],
            "answer": 2
        },
        {
            "id": 6,
            "question": "Which research method typically yields numerical data?",
            "options": [
                "Qualitative Research",
                "Focus Groups",
                "Quantitative Research",
                "Open-ended Interviews"
            ],
            "answer": 2
        },
        {
            "id": 7,
            "question": "Surveys with closed-ended questions are given as an example of which research method?",
            "options": [
                "Qualitative Research",
                "Secondary Research",
                "Observational Research",
                "Quantitative Research"
            ],
            "answer": 3
        },
        {
            "id": 8,
            "question": "Which research method yields non-numerical insights, such as understanding opinions or motivations?",
            "options": [
                "Quantitative Research",
                "Statistical Analysis",
                "Qualitative Research",
                "Numerical Surveys"
            ],
            "answer": 2
        },
        {
            "id": 9,
            "question": "According to the passage, which of the following is a purpose of market research?",
            "options": [
                "To solely increase employee morale",
                "To design company logos",
                "To identify target audiences and evaluate competitors",
                "To manage internal company finances"
            ],
            "answer": 2
        },
        {
            "id": 10,
            "question": "In the story, the company used survey data for what purpose?",
            "options": [
                "To set the marketing budget",
                "To refine product features based on customer satisfaction",
                "To choose a new advertising agency",
                "To analyze stock market trends"
            ],
            "answer": 1
        }
    ]
}

# --- Routes ---
@app.route('/')
def index():
    # Serves the index.html file from the root directory.
    return send_from_directory('.', 'index.html')

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """
    Authenticates a user and checks if they have already submitted the quiz.
    Expects a JSON payload with "username" and "password".
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    # Check credentials against mock user data
    if username in MOCK_USERS_BACKEND and MOCK_USERS_BACKEND[username] == password:
        # Check if user has already submitted the quiz
        if username in SUBMITTED_QUIZZES:
            return jsonify({
                "success": False, # Indicate login itself was fine, but quiz already taken
                "quiz_already_taken": True,
                "message": "You have already completed this quiz. Multiple attempts are not allowed."
            }), 200 # Using 200 OK as the login was valid, but with a specific message
        
        # Login successful and quiz not yet taken
        return jsonify({"success": True, "message": "Login successful", "username": username}), 200
    else:
        # Login failed
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.route('/api/quiz', methods=['GET'])
def get_quiz():
    """
    Serves the quiz questions, title, and time limit.
    Answers are not sent to the frontend.
    """
    # This endpoint could also check if the user (identified by a session/token in a real app)
    # has already taken the quiz, as an additional layer of check before sending questions.
    # For this mock setup, the check is primarily at login and submission.

    questions_for_frontend = []
    for q in quiz_content["questions"]:
        questions_for_frontend.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"]
        })
    return jsonify({
        "title": quiz_content["title"],
        "timeLimit": quiz_content["timeLimit"],
        "questions": questions_for_frontend
    })

@app.route('/api/submit', methods=['POST'])
def submit_quiz():
    """
    Receives quiz answers, calculates the score, and returns results.
    Marks the quiz as submitted for the user.
    Expects a JSON payload with "username" and "answers".
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
        
    username = data.get('username', 'Anonymous')
    user_answers = data.get('answers', [])

    # Double-check if quiz was already submitted, though primary check is at login
    if username in SUBMITTED_QUIZZES and username != 'Anonymous': # Don't block anonymous if that's a use case
        return jsonify({
            "success": False,
            "message": "This quiz has already been submitted by you."
        }), 403 # Forbidden

    score = 0
    total_questions = len(quiz_content["questions"])

    for i, question_data in enumerate(quiz_content["questions"]):
        correct_answer_index = question_data["answer"]
        user_answer_index = None
        if i < len(user_answers) and user_answers[i] is not None:
            try:
                user_answer_index = int(user_answers[i])
            except (ValueError, TypeError):
                user_answer_index = None

        if user_answer_index == correct_answer_index:
            score += 1

    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Add user to the set of submitted quizzes if they are not Anonymous
    if username != 'Anonymous':
        SUBMITTED_QUIZZES.add(username)
        print(f"User {username} added to submitted list. Current list: {SUBMITTED_QUIZZES}")
    
    feedback = ""
    if percentage == 100:
        feedback = f"Perfect score, {username}! You're a market research whiz!"
    elif percentage >= 80:
        feedback = f"Excellent work, {username}! You have a strong understanding."
    elif percentage >= 60:
        feedback = f"Good job, {username}! You're getting the hang of it."
    elif percentage >= 40:
        feedback = f"Not bad, {username}. A little more study and you'll ace it!"
    else:
        feedback = f"Keep learning, {username}! Market research is a valuable skill."

    print(f"Quiz submitted by: {username}, Score: {score}/{total_questions}, Percentage: {percentage:.2f}%")

    return jsonify({
        "success": True,
        "username": username,
        "score": score,
        "totalQuestions": total_questions,
        "percentage": percentage,
        "feedback": feedback
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)