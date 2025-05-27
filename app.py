from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS # For handling Cross-Origin Resource Sharing
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing
from flask_mail import Mail, Message # For sending emails
import os # For environment variables (recommended for credentials)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app) # Enable CORS for all routes. For production, restrict to your frontend's domain.

# --- Email Configuration ---
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
# These are now treated as potentially usable defaults if not overridden by environment variables.
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'rehmanpranto@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'hezp aujt tcxt ezol')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)

# --- User Data Store (Simulating a User Database) ---
USER_ACCOUNTS = {}
SUBMITTED_QUIZZES = set()

# --- Quiz Content ---
quiz_content = {
    "title": "Market Research and Marketing Mix Quiz",
    "timeLimit": 1200,
    "questions": [
        {
            "id": 1,
            "question": "What is the primary purpose of market research?",
            "options": [
                "To increase company profits immediately",
                "To gather, analyze, and interpret data about markets to inform business decisions",
                "To create advertising campaigns",
                "To hire new employees"
            ],
            "answer": 1
        },
        {
            "id": 2,
            "question": "Which of the following is an example of primary research?",
            "options": [
                "Reading industry reports",
                "Analyzing government statistics",
                "Conducting surveys with customers",
                "Reviewing competitor websites"
            ],
            "answer": 2
        },
        {
            "id": 3,
            "question": "What type of research involves analyzing existing data from reports and online sources?",
            "options": [
                "Primary research",
                "Secondary research",
                "Qualitative research",
                "Quantitative research"
            ],
            "answer": 1
        },
        {
            "id": 4,
            "question": "Which research method focuses on numerical data and closed-ended questions?",
            "options": [
                "Qualitative research",
                "Observational research",
                "Quantitative research",
                "Focus group research"
            ],
            "answer": 2
        },
        {
            "id": 5,
            "question": "What are the 4Ps of marketing collectively known as?",
            "options": [
                "Marketing strategy",
                "Marketing mix",
                "Marketing plan",
                "Marketing framework"
            ],
            "answer": 1
        },
        {
            "id": 6,
            "question": "Which of the following is NOT one of the 4Ps of marketing?",
            "options": [
                "Product",
                "Price",
                "People",
                "Place"
            ],
            "answer": 2
        },
        {
            "id": 7,
            "question": "The \"Product\" element of the marketing mix includes all of the following EXCEPT:",
            "options": [
                "Design and features",
                "Quality and branding",
                "Distribution channels",
                "Packaging and warranties"
            ],
            "answer": 2
        },
        {
            "id": 8,
            "question": "What factors should be considered when determining the \"Price\" element?",
            "options": [
                "Production costs only",
                "Competitor pricing only",
                "Production costs, competitor pricing, perceived value, and profit margins",
                "Customer demographics only"
            ],
            "answer": 2
        },
        {
            "id": 9,
            "question": "The \"Place\" element of the marketing mix primarily focuses on:",
            "options": [
                "Where advertisements are placed",
                "How and where customers can access the product",
                "The physical location of the company",
                "The price point of the product"
            ],
            "answer": 1
        },
        {
            "id": 10,
            "question": "Which of the following best describes the \"Promotion\" element?",
            "options": [
                "Price discounts and sales",
                "Product development activities",
                "Communication strategies to inform and persuade customers",
                "Distribution logistics"
            ],
            "answer": 2
        },
        {
            "id": 11,
            "question": "What is a key benefit of conducting market research?",
            "options": [
                "Guaranteeing product success",
                "Eliminating all business risks",
                "Understanding consumer needs and behaviors",
                "Reducing production costs"
            ],
            "answer": 2
        },
        {
            "id": 12,
            "question": "Which research method would be best for gathering detailed, non-numerical insights?",
            "options": [
                "Online surveys with multiple choice questions",
                "Statistical analysis of sales data",
                "Open-ended interviews",
                "Quantitative polling"
            ],
            "answer": 2
        },
        {
            "id": 13,
            "question": "What is one purpose of market research mentioned in the text?",
            "options": [
                "To hire marketing staff",
                "To assess market size and potential",
                "To design company logos",
                "To choose office locations"
            ],
            "answer": 1
        },
        {
            "id": 14,
            "question": "The 4Ps of marketing must be:",
            "options": [
                "Considered independently",
                "Managed by different departments",
                "Considered cohesively for effective strategy",
                "Changed frequently"
            ],
            "answer": 2
        },
        {
            "id": 15,
            "question": "Which promotional tool is NOT mentioned in the text?",
            "options": [
                "Advertising",
                "Public relations",
                "Telemarketing",
                "Social media marketing"
            ],
            "answer": 2
        },
        {
            "id": 16,
            "question": "An example of qualitative research would be:",
            "options": [
                "A survey asking customers to rate satisfaction on a scale of 1-10",
                "Counting how many people visit a store daily",
                "Focus groups discussing product preferences",
                "Analyzing website traffic statistics"
            ],
            "answer": 2
        },
        {
            "id": 17,
            "question": "What does market research help businesses evaluate regarding competitors?",
            "options": [
                "Their employee satisfaction",
                "Their strengths and weaknesses",
                "Their office locations",
                "Their hiring practices"
            ],
            "answer": 1
        },
        {
            "id": 18,
            "question": "The \"Place\" element is also known as:",
            "options": [
                "Promotion",
                "Distribution",
                "Positioning",
                "Pricing"
            ],
            "answer": 1
        },
        {
            "id": 19,
            "question": "Which statement about the marketing mix is true?",
            "options": [
                "Each element works independently",
                "Price is the most important element",
                "All four elements are interconnected",
                "Promotion should be the primary focus"
            ],
            "answer": 2
        },
        {
            "id": 20,
            "question": "What is the ultimate goal of the promotion element?",
            "options": [
                "To reduce production costs",
                "To build awareness, generate interest, and drive sales",
                "To improve product quality",
                "To expand distribution channels"
            ],
            "answer": 1
        }
    ]
}

# --- Routes ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"success": False, "message": "Invalid email format"}), 400
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long"}), 400
    if email in USER_ACCOUNTS:
        return jsonify({"success": False, "message": "Email already registered"}), 409
    hashed_password = generate_password_hash(password)
    USER_ACCOUNTS[email] = hashed_password
    print(f"New user registered: {email}")
    return jsonify({"success": True, "message": "Registration successful. Please login."}), 201

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    stored_hashed_password = USER_ACCOUNTS.get(email)
    if stored_hashed_password and check_password_hash(stored_hashed_password, password):
        if email in SUBMITTED_QUIZZES:
            return jsonify({
                "success": False,
                "quiz_already_taken": True,
                "message": "You have already completed this quiz. Multiple attempts are not allowed."
            }), 200
        return jsonify({"success": True, "message": "Login successful", "email": email}), 200
    else:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

@app.route('/api/quiz', methods=['GET'])
def get_quiz():
    questions_for_frontend = []
    for q_idx, q in enumerate(quiz_content["questions"]): # Use enumerate for index if needed elsewhere
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
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    user_email = data.get('email')
    user_answers = data.get('answers', [])
    if not user_email:
        return jsonify({"success": False, "message": "User email not provided with submission."}), 400
    if user_email not in USER_ACCOUNTS:
        return jsonify({"success": False, "message": "Unauthorized user or user not found."}), 401
    if user_email in SUBMITTED_QUIZZES:
        return jsonify({
            "success": False,
            "message": "This quiz has already been submitted by you."
        }), 403

    score = 0
    total_questions = len(quiz_content["questions"])
    for i, question_data in enumerate(quiz_content["questions"]):
        correct_answer_index = question_data["answer"]
        user_selected_index = None
        if i < len(user_answers) and user_answers[i] is not None:
            try:
                user_selected_index = int(user_answers[i])
            except (ValueError, TypeError):
                user_selected_index = None # Invalid answer format, treat as incorrect
        if user_selected_index == correct_answer_index:
            score += 1

    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    SUBMITTED_QUIZZES.add(user_email) # Mark quiz as submitted for this user
    print(f"User {user_email} added to submitted list. Current list: {SUBMITTED_QUIZZES}")

    feedback_name = user_email.split('@')[0] # Simple way to get a name part
    feedback = ""
    if percentage == 100:
        feedback = f"Perfect score, {feedback_name}! You're a market research whiz!"
    elif percentage >= 80:
        feedback = f"Excellent work, {feedback_name}! You have a strong understanding."
    elif percentage >= 60:
        feedback = f"Good job, {feedback_name}! You're getting the hang of it."
    elif percentage >= 40:
        feedback = f"Not bad, {feedback_name}. A little more study and you'll ace it!"
    else:
        feedback = f"Keep learning, {feedback_name}! Market research is a valuable skill."

    print(f"Quiz submitted by: {user_email}, Score: {score}/{total_questions}, Percentage: {percentage:.2f}%")

    # --- Send Email Report ---
    admin_email_recipient = "rehmanpranto@gmail.com" # Fixed admin email, can be an env variable too
    email_recipients_list = [admin_email_recipient, user_email]

    email_subject = f"Quiz Results for {user_email} - {quiz_content['title']}"

    email_body_text = f"""
    Hello {feedback_name},

    Here are your results for the quiz: "{quiz_content['title']}".

    User Email: {user_email}
    Score: {score}/{total_questions}
    Percentage: {percentage:.2f}%
    Feedback: {feedback}

    This report was also sent to the site administrator.

    Thank you for participating!
    """

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
    """

    try:
        # MODIFIED CHECK:
        # Skip sending only if MAIL_USERNAME or MAIL_PASSWORD are not set,
        # or if they are set to very generic placeholders that must be changed.
        mail_user = app.config.get('MAIL_USERNAME')
        mail_pass = app.config.get('MAIL_PASSWORD')

        # Check for truly unconfigured or generic placeholder credentials
        if not mail_user or not mail_pass or \
           mail_user == 'YOUR_SENDER_EMAIL@example.com' or \
           mail_pass == 'YOUR_GMAIL_APP_PASSWORD': # Use generic placeholders for this check

            warning_message = "WARNING: Email credentials are not properly configured. "
            if mail_user == 'YOUR_SENDER_EMAIL@example.com' or \
               mail_pass == 'YOUR_GMAIL_APP_PASSWORD':
                warning_message += "Default generic placeholders detected. "
            elif not mail_user or not mail_pass: # Check if they are simply empty
                warning_message += "MAIL_USERNAME or MAIL_PASSWORD is significantly missing. "
            warning_message += "Skipping email sending."
            print(warning_message)
            print(f"Current MAIL_USERNAME used for check: {mail_user}") # For debugging
        else:
            # Credentials seem to be present and not the generic placeholders, attempt sending.
            msg = Message(subject=email_subject,
                          recipients=email_recipients_list,
                          body=email_body_text,
                          html=email_body_html,
                          sender=app.config['MAIL_DEFAULT_SENDER'])
            mail.send(msg)
            print(f"Report email sent successfully to {', '.join(email_recipients_list)}")
    except Exception as e:
        print(f"Error sending email: {e}")
        # Log this error formally in a production app.
        # The quiz result is still returned to the user even if email fails.

    return jsonify({
        "success": True,
        "email": user_email,
        "score": score,
        "totalQuestions": total_questions,
        "percentage": percentage,
        "feedback": feedback
    })

if __name__ == '__main__':
    print(f"Attempting to use MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")

    # MODIFIED STARTUP CHECK (Corrected):
    mail_user_startup = app.config.get('MAIL_USERNAME')
    mail_pass_startup = app.config.get('MAIL_PASSWORD')

    # Corrected the unterminated string literal in the line below
    if not mail_user_startup or not mail_pass_startup or \
       mail_user_startup == 'YOUR_SENDER_EMAIL@example.com' or \
       mail_pass_startup == 'YOUR_GMAIL_APP_PASSWORD': # This was the corrected line
        print("\n*********************************************************************")
        print("WARNING: Email sending might be disabled or use default generic placeholders.")
        print("Please ensure MAIL_USERNAME and MAIL_PASSWORD are correctly set")
        print("(preferably as environment variables) for reliable email functionality.")
        if mail_user_startup == 'YOUR_SENDER_EMAIL@example.com' or \
           mail_pass_startup == 'YOUR_GMAIL_APP_PASSWORD':
            print("Default generic placeholder credentials detected.")
        elif not mail_user_startup or not mail_pass_startup: # Check if they are simply empty
            print("MAIL_USERNAME or MAIL_PASSWORD seems to be missing or empty.")
        print(f"Currently configured MAIL_USERNAME for startup check: {mail_user_startup}")
        print("*********************************************************************\n")
    else:
        print("Email credentials appear to be configured.") # This should print if your specific credentials are set

    app.run(debug=True, port=5001)