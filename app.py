from flask import Flask, jsonify, request, send_from_directory, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import os
import psycopg2
import psycopg2.extras # For dictionary cursors
import json
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv() # Call load_dotenv() at the top

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# --- Database Configuration ---
app.config['DB_HOST'] = os.environ.get('DB_HOST', 'localhost')
app.config['DB_NAME'] = os.environ.get('DB_NAME', 'quizflow_db')
app.config['DB_USER'] = os.environ.get('DB_USER', 'your_db_user')
app.config['DB_PASSWORD'] = os.environ.get('DB_PASSWORD', 'your_db_password')
app.config['DB_PORT'] = os.environ.get('DB_PORT', '5432')

# --- Email Configuration ---
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])
ADMIN_EMAIL_RECIPIENT = os.environ.get('ADMIN_EMAIL_RECIPIENT', 'rehmanpranto@gmail.com')

mail = Mail(app)

# --- Database Helper Functions ---
def get_db_connection():
    if 'db_conn' not in g:
        try:
            g.db_conn = psycopg2.connect(
                host=app.config['DB_HOST'],
                dbname=app.config['DB_NAME'],
                user=app.config['DB_USER'],
                password=app.config['DB_PASSWORD'],
                port=app.config['DB_PORT']
            )
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL database: {e}")
            raise
    return g.db_conn

@app.teardown_appcontext
def close_db_connection(exception=None):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

CURRENT_QUIZ_ID = 1 # Assuming we are working with quiz_id = 1 from the 'quizzes' table

# --- Routes ---
@app.route('/')
def index_page():
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

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s;", (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Email already registered"}), 409

        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s);", (email, hashed_password))
        conn.commit()
        print(f"New user registered: {email}")
        return jsonify({"success": True, "message": "Registration successful. Please login."}), 201
    except psycopg2.Error as e:
        if conn: conn.rollback()
        print(f"Database error during registration: {e}")
        return jsonify({"success": False, "message": "Registration failed due to a server error."}), 500
    except Exception as e:
        print(f"An error occurred during registration: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500
    finally:
        if cursor: cursor.close()

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT id, password_hash FROM users WHERE email = %s;", (email,))
        user_record = cursor.fetchone()

        if user_record and check_password_hash(user_record['password_hash'], password):
            user_id = user_record['id']
            
            cursor.execute(
                "SELECT id, score, total_questions_in_quiz, percentage, feedback_text "
                "FROM quiz_submissions WHERE user_id = %s AND quiz_id = %s;",
                (user_id, CURRENT_QUIZ_ID) # Check for the default quiz
            )
            submission_record = cursor.fetchone()

            quiz_title_for_past_result = "Quiz Results" # Default title
            cursor.execute("SELECT title FROM quizzes WHERE id = %s;", (CURRENT_QUIZ_ID,))
            quiz_info = cursor.fetchone()
            if quiz_info:
                quiz_title_for_past_result = quiz_info['title']
            
            if submission_record: # For the default quiz
                return jsonify({
                    "success": True, 
                    "quiz_already_taken": True, # Specifically for the default quiz
                    "message": "You have already completed this quiz. Here are your previous results.",
                    "email": email,
                    "user_id": user_id,
                    "past_results": { # For the default quiz
                        "submission_id": submission_record['id'],
                        "quizTitle": quiz_title_for_past_result,
                        "score": submission_record['score'],
                        "totalQuestions": submission_record['total_questions_in_quiz'],
                        "percentage": float(submission_record['percentage']), 
                        "feedback": submission_record['feedback_text']
                    }
                }), 200
            else:
                return jsonify({"success": True, "message": "Login successful. You can start the quiz.", "email": email, "user_id": user_id}), 200
        else:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401
    except psycopg2.Error as e:
        print(f"Database error during login: {e}")
        return jsonify({"success": False, "message": "Login failed due to a server error."}), 500
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500
    finally:
        if cursor: cursor.close()

@app.route('/api/quiz', methods=['GET'])
def get_quiz():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("SELECT title, time_limit_seconds FROM quizzes WHERE id = %s;", (CURRENT_QUIZ_ID,))
        quiz_meta = cursor.fetchone()
        if not quiz_meta:
            return jsonify({"success": False, "message": "Quiz not found"}), 404

        cursor.execute(
            "SELECT original_quiz_content_id as id, question_text as question, options "
            "FROM questions WHERE quiz_id = %s ORDER BY original_quiz_content_id ASC;", (CURRENT_QUIZ_ID,)
        )
        questions_from_db = cursor.fetchall()

        questions_for_frontend = []
        for q_db in questions_from_db:
            questions_for_frontend.append({
                "id": q_db["id"], 
                "question": q_db["question"],
                "options": q_db["options"]
            })
        
        return jsonify({
            "title": quiz_meta["title"],
            "timeLimit": quiz_meta["time_limit_seconds"],
            "questions": questions_for_frontend
        })
    except psycopg2.Error as e:
        print(f"Database error fetching quiz: {e}")
        return jsonify({"success": False, "message": "Error fetching quiz data."}), 500
    except Exception as e:
        print(f"An error occurred fetching quiz: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500
    finally:
        if cursor: cursor.close()

@app.route('/api/submit', methods=['POST'])
def submit_quiz():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    user_email = data.get('email')
    user_answers_indices = data.get('answers', []) 

    if not user_email:
        return jsonify({"success": False, "message": "User email not provided with submission."}), 400

    conn = None
    cursor = None
    submission_id = None 

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("SELECT id FROM users WHERE email = %s;", (user_email,))
        user_record = cursor.fetchone()
        if not user_record:
            return jsonify({"success": False, "message": "Unauthorized user or user not found."}), 401
        user_id = user_record['id']

        cursor.execute("SELECT id FROM quiz_submissions WHERE user_id = %s AND quiz_id = %s;", (user_id, CURRENT_QUIZ_ID))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "This quiz has already been submitted by you."}), 403

        cursor.execute(
            "SELECT id, original_quiz_content_id, question_text, options, correct_option_index "
            "FROM questions WHERE quiz_id = %s ORDER BY original_quiz_content_id ASC;", (CURRENT_QUIZ_ID,)
        )
        db_questions = cursor.fetchall()

        if not db_questions:
            return jsonify({"success": False, "message": "Quiz questions not found for score calculation."}), 500

        score = 0
        total_questions = len(db_questions)
        detailed_results_for_response_and_email = []
        
        ordered_db_questions = db_questions

        for i, question_data_from_db in enumerate(ordered_db_questions):
            db_question_id = question_data_from_db["id"] 
            correct_answer_index_from_db = question_data_from_db["correct_option_index"]
            question_options_from_db = question_data_from_db["options"]
            
            user_selected_index = None
            user_selected_text = "Not Answered"
            is_correct_flag = False

            if i < len(user_answers_indices) and user_answers_indices[i] is not None:
                try:
                    user_selected_index = int(user_answers_indices[i])
                    if 0 <= user_selected_index < len(question_options_from_db):
                        user_selected_text = question_options_from_db[user_selected_index]
                    else:
                        user_selected_text = "Invalid Option Selected"
                except (ValueError, TypeError):
                    user_selected_text = "Invalid Answer Format"
            
            if user_selected_index == correct_answer_index_from_db:
                score += 1
                is_correct_flag = True
            
            detailed_results_for_response_and_email.append({
                "original_question_id": question_data_from_db["original_quiz_content_id"],
                "db_question_id": db_question_id, 
                "question": question_data_from_db["question_text"],
                "your_answer_text": user_selected_text,
                "your_answer_index": user_selected_index, 
                "correct_answer_text": question_options_from_db[correct_answer_index_from_db],
                "is_correct": is_correct_flag
            })

        percentage = (score / total_questions) * 100 if total_questions > 0 else 0
        
        feedback_name = user_email.split('@')[0]
        feedback_text = "" # Calculate feedback text as before
        if percentage == 100: feedback_text = f"Perfect score, {feedback_name}! You're a market research whiz!"
        elif percentage >= 80: feedback_text = f"Excellent work, {feedback_name}! You have a strong understanding."
        elif percentage >= 60: feedback_text = f"Good job, {feedback_name}! You're getting the hang of it."
        elif percentage >= 40: feedback_text = f"Not bad, {feedback_name}. A little more study and you'll ace it!"
        else: feedback_text = f"Keep learning, {feedback_name}! Market research is a valuable skill."


        cursor.execute(
            "INSERT INTO quiz_submissions (user_id, quiz_id, score, total_questions_in_quiz, percentage, feedback_text) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
            (user_id, CURRENT_QUIZ_ID, score, total_questions, percentage, feedback_text)
        )
        submission_id_tuple = cursor.fetchone()
        if not submission_id_tuple:
            if conn: conn.rollback()
            return jsonify({"success": False, "message": "Failed to save quiz submission."}), 500
        submission_id = submission_id_tuple['id']

        for item_result in detailed_results_for_response_and_email:
            cursor.execute(
                "INSERT INTO submission_answers (quiz_submission_id, question_id, user_selected_option_index, is_correct) "
                "VALUES (%s, %s, %s, %s);",
                (submission_id, item_result["db_question_id"], item_result["your_answer_index"], item_result["is_correct"])
            )
        
        conn.commit()
        print(f"Quiz submitted by: {user_email}, Score: {score}/{total_questions}, Submission ID: {submission_id}")

        # --- Prepare Email Content ---
        detailed_results_text_for_email_only = "\n\n--- Detailed Breakdown ---\n"
        detailed_results_html_for_email_only = "<h3>Detailed Breakdown:</h3><ul>"
        for item in detailed_results_for_response_and_email:
            status_symbol = "✔" if item['is_correct'] else "✘"
            detailed_results_text_for_email_only += (
                f"\nQ: {item['question']}\n"
                f"Your Answer: {item['your_answer_text']} {status_symbol}\n" 
                f"Correct Answer: {item['correct_answer_text']}\n" 
            )
            detailed_results_html_for_email_only += (
                f"<li>"
                f"<p><strong>Q: {item['question']}</strong></p>"
                f"<p>Your Answer: {item['your_answer_text']} <span style='color: {'green' if item['is_correct'] else 'red'}; font-weight: bold;'>{status_symbol}</span></p>" 
                f"<p>Correct Answer: {item['correct_answer_text']}</p>" 
                f"</li>"
            )
        detailed_results_html_for_email_only += "</ul>"
        
        quiz_title_for_email = "Quiz"
        cursor.execute("SELECT title FROM quizzes WHERE id = %s;", (CURRENT_QUIZ_ID,))
        quiz_info_for_email = cursor.fetchone()
        if quiz_info_for_email:
            quiz_title_for_email = quiz_info_for_email['title']

        if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
            email_recipients_list = [ADMIN_EMAIL_RECIPIENT]
            if user_email != ADMIN_EMAIL_RECIPIENT:
                 email_recipients_list.append(user_email)
            email_subject = f"Quiz Results for {user_email} - {quiz_title_for_email}"
            email_body_text = f"Hello {feedback_name},\n\nHere are your results for the quiz: \"{quiz_title_for_email}\".\n\nUser Email: {user_email}\nScore: {score}/{total_questions}\nPercentage: {percentage:.2f}%\nFeedback: {feedback_text}\n{detailed_results_text_for_email_only}\nThis report was also sent to the site administrator.\n\nThank you for participating!"
            email_body_html = f"<html><body><p>Hello {feedback_name},</p><p>Here are your results for the quiz: \"<strong>{quiz_title_for_email}</strong>\".</p><ul><li><strong>User Email:</strong> {user_email}</li><li><strong>Score:</strong> {score}/{total_questions}</li><li><strong>Percentage:</strong> {percentage:.2f}%</li><li><strong>Feedback:</strong> {feedback_text}</li></ul>{detailed_results_html_for_email_only}<p>This report was also sent to the site administrator.</p><p>Thank you for participating!</p></body></html>"
            try:
                msg = Message(subject=email_subject, recipients=email_recipients_list, body=email_body_text, html=email_body_html, sender=app.config['MAIL_DEFAULT_SENDER'])
                mail.send(msg)
                print(f"Report email sent successfully to {', '.join(email_recipients_list)}")
            except Exception as e:
                print(f"Error sending email: {e}")
        else:
            print("Email credentials (MAIL_USERNAME or MAIL_PASSWORD) not configured. Skipping email sending.")

        response_detailed_results_for_frontend = [
            {
                "id": item["original_question_id"],
                "question": item["question"],
                "your_answer": item["your_answer_text"],
                "correct_answer": item["correct_answer_text"],
                "is_correct": item["is_correct"]
            } for item in detailed_results_for_response_and_email
        ]
        return jsonify({
            "success": True, "email": user_email, "submission_id": submission_id,
            "score": score, "totalQuestions": total_questions, "percentage": percentage,
            "feedback": feedback_text, "detailed_results": response_detailed_results_for_frontend
        })
    except psycopg2.Error as e:
        if conn: conn.rollback()
        print(f"Database error during submission: {e}")
        return jsonify({"success": False, "message": "Quiz submission failed due to a server error."}), 500
    except Exception as e:
        if conn: conn.rollback()
        print(f"An error occurred during submission: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred during submission."}), 500
    finally:
        if cursor: cursor.close()

@app.route('/api/user/submissions', methods=['GET'])
def get_user_submissions():
    user_email = request.args.get('email') 
    if not user_email:
        return jsonify({"success": False, "message": "User email parameter is required."}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("SELECT id FROM users WHERE email = %s;", (user_email,))
        user_record = cursor.fetchone()
        if not user_record:
            return jsonify({"success": False, "message": "User not found."}), 404
        user_id = user_record['id']

        cursor.execute("""
            SELECT 
                qs.id as submission_id, qs.quiz_id, q.title as quiz_title, 
                qs.score, qs.total_questions_in_quiz, qs.percentage, qs.submitted_at
            FROM quiz_submissions qs
            JOIN quizzes q ON qs.quiz_id = q.id
            WHERE qs.user_id = %s
            ORDER BY qs.submitted_at DESC;
        """, (user_id,))
        submissions_raw = cursor.fetchall()
        
        submissions_list = []
        for sub_row in submissions_raw:
            sub_dict = dict(sub_row)
            sub_dict['submitted_at'] = sub_dict['submitted_at'].isoformat() if sub_dict.get('submitted_at') else None
            sub_dict['percentage'] = float(sub_dict['percentage']) if sub_dict.get('percentage') is not None else None
            submissions_list.append(sub_dict)
        return jsonify({"success": True, "submissions": submissions_list})
    except psycopg2.Error as e:
        print(f"Database error fetching user submissions: {e}")
        return jsonify({"success": False, "message": "Error fetching submissions."}), 500
    except Exception as e:
        print(f"An error occurred fetching user submissions: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500
    finally:
        if cursor: cursor.close()

@app.route('/api/submission/<int:submission_id>/details', methods=['GET'])
def get_submission_details(submission_id):
    # Note: Add user authentication/authorization here in a real app
    # to ensure the requesting user is allowed to see this submission.
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("""
            SELECT qs.id as submission_id, qs.quiz_id, q.title as quiz_title, 
                   qs.score, qs.total_questions_in_quiz, qs.percentage, qs.feedback_text,
                   qs.submitted_at, u.email as user_email
            FROM quiz_submissions qs
            JOIN quizzes q ON qs.quiz_id = q.id
            JOIN users u ON qs.user_id = u.id
            WHERE qs.id = %s;
        """, (submission_id,))
        submission_summary_raw = cursor.fetchone()

        if not submission_summary_raw:
            return jsonify({"success": False, "message": "Submission not found."}), 404
        
        summary_dict = dict(submission_summary_raw)
        summary_dict['submitted_at'] = summary_dict['submitted_at'].isoformat() if summary_dict.get('submitted_at') else None
        summary_dict['percentage'] = float(summary_dict['percentage']) if summary_dict.get('percentage') is not None else None


        cursor.execute("""
            SELECT sa.question_id, q_text.question_text, q_text.options as question_options,
                   q_text.correct_option_index, sa.user_selected_option_index, sa.is_correct
            FROM submission_answers sa
            JOIN questions q_text ON sa.question_id = q_text.id
            WHERE sa.quiz_submission_id = %s
            ORDER BY q_text.original_quiz_content_id ASC;
        """, (submission_id,))
        answers_details_raw = cursor.fetchall()

        detailed_questions_list = []
        for ad_row in answers_details_raw:
            ad = dict(ad_row)
            user_answer_text = "Not Answered"
            if ad.get('user_selected_option_index') is not None and \
               ad.get('question_options') and \
               0 <= ad['user_selected_option_index'] < len(ad['question_options']):
                user_answer_text = ad['question_options'][ad['user_selected_option_index']]
            
            correct_answer_text = "N/A"
            if ad.get('question_options') and ad.get('correct_option_index') is not None and \
               0 <= ad['correct_option_index'] < len(ad['question_options']):
                correct_answer_text = ad['question_options'][ad['correct_option_index']]

            detailed_questions_list.append({
                "question_id": ad['question_id'], "question_text": ad['question_text'],
                "user_selected_answer_index": ad.get('user_selected_option_index'),
                "user_selected_answer_text": user_answer_text,
                "correct_answer_index": ad.get('correct_option_index'),
                "correct_answer_text": correct_answer_text, "is_correct": ad['is_correct']
            })
        return jsonify({"success": True, "summary": summary_dict, "details": detailed_questions_list})
    except psycopg2.Error as e:
        print(f"Database error fetching submission details: {e}")
        return jsonify({"success": False, "message": "Error fetching submission details."}), 500
    except Exception as e:
        print(f"An error occurred fetching submission details: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500
    finally:
        if cursor: cursor.close()

if __name__ == '__main__':
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print("\n*********************************************************************")
        print("WARNING: Email sending might be disabled.") # Simplified warning
        print("Please ensure MAIL_USERNAME and MAIL_PASSWORD are correctly set in .env")
        print("*********************************************************************\n")
    else:
        print("Email credentials appear to be configured.")

    print(f"Admin email for reports: {ADMIN_EMAIL_RECIPIENT}")
    print(f"Attempting to connect to DB: {app.config['DB_NAME']} on {app.config['DB_HOST']}:{app.config['DB_PORT']} with user {app.config['DB_USER']}")
    
    conn_test = None
    cursor_test = None
    try:
        conn_test = psycopg2.connect(
                host=app.config['DB_HOST'], dbname=app.config['DB_NAME'],
                user=app.config['DB_USER'], password=app.config['DB_PASSWORD'],
                port=app.config['DB_PORT']
            )
        cursor_test = conn_test.cursor()
        cursor_test.execute("SELECT NOW();")
        time_result = cursor_test.fetchone()
        print(f"Database connection successful on startup. DB Server Time: {time_result[0] if time_result else 'N/A'}")
    except psycopg2.Error as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"FATAL: Database connection failed on startup: {e}")
        print("Check .env: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    finally:
        if cursor_test: cursor_test.close()
        if conn_test: conn_test.close()
    app.run(debug=True, port=5001)