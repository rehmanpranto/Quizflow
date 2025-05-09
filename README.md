# 📊 QuizFlow

**QuizFlow** is a lightweight, web-based quiz platform built with **Flask** and **Vanilla JS + Tailwind CSS** that tests users on their knowledge of *market research fundamentals*. The app includes user login, quiz timer, scoring, and feedback with basic anti-cheating measures.

---

## 🚀 Features

* 🔐 **User Authentication** – Login system using predefined mock credentials.
* 🧠 **Interactive Quiz** – 10-question multiple-choice quiz.
* ⏱️ **Timer** – 15-minute time limit for quiz completion.
* 🧾 **Score & Feedback** – Immediate results and performance-based feedback.
* 🛡️ **Anti-Cheating Measures** – Alerts on tab switching and focus loss.
* 🎨 **Responsive UI** – Clean, accessible interface styled with Tailwind CSS.

---

## 🗂️ Project Structure

```
.
├── app.py             # Flask backend with API routes
├── index.html         # Frontend (UI logic and styling included)
├── requirements.txt   # Python dependencies
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/rehmanpranto/quizflow.git
cd quizflow
```

### 2. Set Up Python Environment

Make sure Python 3.7+ is installed.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the App

```bash
python app.py
```

Access the app at: [http://localhost:5001](http://localhost:5001)

---

## 🔐 Login Credentials

Use one of the following test accounts:

| Username  | Password |
| --------- | -------- |
| student1  | pass123  |
| student01 | pass456  |
| teacher   | admin456 |
| user      | password |

---

## 📦 Dependencies

* [Flask](https://flask.palletsprojects.com/)
* [Flask-CORS](https://flask-cors.readthedocs.io/)

Install via:

```bash
pip install Flask Flask-CORS
```

---

## 📌 Notes

* Data is stored in-memory — restarting the server resets quiz submissions.
* For production use:

  * Replace mock authentication with real user management.
  * Use persistent storage (e.g., SQLite, PostgreSQL).
  * Serve frontend files with a production server (e.g., Nginx).

---

## 🛠️ Future Improvements

* Add admin panel for quiz management.
* Store quiz results in a database.
* Enable dynamic quiz creation and editing.
* Support registration and password reset.

---

## 📄 License

MIT License — Feel free to use, modify, and share.
