# 🚀 QuizFlow: Unleash Your Inner Genius! 🧠✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Ever wondered how much you *really* know? Ready to challenge yourself and track your learning journey like never before? **QuizFlow** is here to transform the way you test your knowledge! This isn't just another quiz app; it's your personal arena for intellectual showdowns, complete with dynamic quizzes, persistent scores, and detailed feedback to help you conquer any topic! [cite: 1]

Dive into an interactive experience built with a powerful **Flask (Python) backend** and a sleek **Vanilla JS & Tailwind CSS frontend**, all powered by a robust **PostgreSQL database** to keep your progress safe and sound. [cite: 1]

---

## 🌟 Features That Make QuizFlow Awesome!

* 🔐 **Rock-Solid User Authentication:** Secure registration and login system to keep your quiz journey personal. [cite: 1]
* 🧠 **Dynamic Interactive Quizzes:** Engage with quizzes pulled directly from our database – always fresh, always challenging! [cite: 1]
* ⏱️ **Beat the Clock:** A built-in timer keeps you on your toes for each quiz session! [cite: 1]
* 📊 **Instant Scores & Insightful Feedback:** Get your results pasiónmediately, with tailored feedback to understand your strengths and areas for growth. [cite: 1]
* 💾 **Persistent Progress with PostgreSQL:** Your user accounts, quiz attempts, scores, and even your specific answers are securely stored. [cite: 1]
* 📜 **Your Quiz History, Unlocked!**
    * View a list of all quizzes you've attempted. [cite: 1]
    * Check your previous scores anytime. [cite: 1]
    * 🔎 **Detailed Answer Review:** Dive deep into past submissions to see exactly which questions you aced and which ones tricked you, along with the correct answers! [cite: 1]
* 📧 **Email Result Notifications:** Get your quiz summaries delivered straight to your inbox (and the admin's!). [cite: 1]
* 🛡️ **Focus Mode:** Basic anti-cheating measures with alerts for tab-switching to help maintain focus.
* 🎨 **Sleek & Responsive UI:** Crafted with Tailwind CSS for a beautiful experience on any device, featuring elegant Playfair Display and readable Roboto fonts.
* 🔧 **Tech Stack:**
    * **Backend:** Python (Flask) [cite: 1]
    * **Frontend:** Vanilla JavaScript, Tailwind CSS, HTML5
    * **Database:** PostgreSQL [cite: 1]
    * **And more:** `python-dotenv`, Flask-CORS, Flask-Mail, Werkzeug.

---

## 🖼️ Sneak Peek (Imagine Awesome Screenshots/GIFs Here!)

* *(Placeholder: ![alt text](<photos\Screenshot 2025-05-25 at 23-17-13 QuizFlow.png>))*
* *(Placeholder: ![alt text](<photos\Screenshot 2025-05-25 at 23-18-14 QuizFlow.png>))*
* *(Placeholder: ![alt text](<photos\Screenshot 2025-05-25 at 23-18-44 QuizFlow.png>))*
* *(Placeholder:![alt text](<photos\Screenshot 2025-05-25 at 23-19-03 QuizFlow.png>))*
* *(Placeholder: ![alt text](<photos\Screenshot 2025-05-25 at 23-19-12 QuizFlow.png>))*

---

## 🗂️ Project Structure
├── app.py             # Flask backend (API routes, DB logic, email)
├── index.html         # Frontend (UI, Vanilla JS logic, Tailwind CSS)
├── requirements.txt   # Python dependencies
├── .env               # !!! IMPORTANT: For your database and mail credentials (Create this file!)
└── README.md          # You are here!
## ⚙️ Get QuizFlow Up & Running!

Ready to start your QuizFlow adventure? Here’s how:

1.  **Clone the Mothership (This Repository):**
    ```bash
    git clone [https://github.com/your-username/quizflow.git](https://github.com/your-username/quizflow.git) # Replace with your repo URL
    cd quizflow
    ```

2.  **Set Up Your Python Universe (Virtual Environment):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the Power-Ups (Dependencies):**
    ```bash
    pip install -r requirements.txt
    ```
    *(This will install Flask, psycopg2-binary, python-dotenv, Flask-CORS, Flask-Mail, Werkzeug, and gunicorn).*

4.  **Awaken the Database (PostgreSQL Setup):**
    * Ensure PostgreSQL is installed and running.
    * Create a new database (e.g., `quizflow_db`).
    * Connect to your database and execute the SQL commands provided (or use your migration scripts) to create the necessary tables: `users`, `quizzes`, `questions`, `quiz_submissions`, `submission_answers`.
    * **Crucial:** Populate your `quizzes` and `questions` tables with at least one quiz and its questions for the app to function correctly.

5.  **Configure Your Secrets (`.env` file):**
    * Create a `.env` file in the root of the project.
    * Add your database and email credentials. This file is loaded by `app.py` to configure the application. **Do NOT commit your `.env` file to version control!**
        ```env
        # --- Database Credentials ---
        DB_HOST=your_db_host (e.g., localhost or your Supabase host)
        DB_NAME=your_db_name (e.g., quizflow_db or postgres)
        DB_USER=your_db_user
        DB_PASSWORD=your_super_secret_db_password
        DB_PORT=your_db_port (e.g., 5432 or 6543 for Supabase pooler)

        # --- Email Credentials (Optional, for sending result emails) ---
        MAIL_SERVER=smtp.example.com
        MAIL_PORT=587
        MAIL_USE_TLS=true
        MAIL_USE_SSL=false
        MAIL_USERNAME=your-email@example.com
        MAIL_PASSWORD=your-email-password-or-app-password
        MAIL_DEFAULT_SENDER=your-email@example.com
        ADMIN_EMAIL_RECIPIENT=admin-email@example.com
        ```

6.  **Launch!**
    ```bash
    python app.py
    ```
    Open your browser and navigate to: `http://127.0.0.1:5001` (or the address shown in your terminal).

---

## 🔑 User Accounts

* 🚀 **Self-Registration:** Users can create their own accounts directly within the app! [cite: 1]

---

## 🛠️ Future Enhancements & Galactic Conquests!

QuizFlow is already cool, but the universe is vast! Here’s what’s on the horizon:

* 👑 **Admin Command Center:** A dedicated panel for creating, editing, and managing quizzes with god-like ease.
* 🎭 **More Quiz Flavors:** Support for different question types (fill-in-the-blanks, matching, etc.).
* 📈 **Enhanced User Dashboards:** Visual progress tracking and performance analytics.
* 🛡️ **Fort Knox Security:** Implementation of JWT/Session-based authentication for even tighter security.
* 🔑 **"Oops, I Forgot!" Button:** Password reset functionality.
* 🌐 **Multilingual Support:** Quizzes for everyone, everywhere!
* 🤝 **Team Challenges:** Group quiz modes for collaborative fun.

---

## 🤝 Contributing

Got ideas to make QuizFlow even more epic? Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` file (if you add one) or the shield at the top for more information.

---

**Now go forth and quiz like you've never quizzed before!** 🌟