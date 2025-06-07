# GemSpark
A full-stack chatbot application built with Streamlit, MongoDB, and Google's Gemini LLM. This project enables real-time conversation using generative AI while managing user authentication and persistent chat sessions.

## Features
- **User Login & Registration** system (with `bcrypt` password hashing)
- **Persistent Chat History** (stored and loaded from MongoDB)
- Manage **multiple chat sessions** (create, rename, delete)
- Real-time conversation with **Gemini 1.5 Flash (LLM)**
- Uses **Google Generative AI API** via `google.generativeai`
- Built with **Streamlit** for a sleek UI experience
- Fully modular backend using **MongoDB**, **dotenv**, and Python

## Skills & Technologies Used

| Category           | Technologies / Concepts                                       |
|--------------------|---------------------------------------------------------------|
| LLM Integration    | Google Gemini API (Generative AI), Prompt Engineering         |
| Backend Logic      | Python, MongoDB, bcrypt, LangChain-style history formatting   |
| API Usage          | Google Generative AI SDK (`google.generativeai`)              |
| Auth & Security    | Login/Register system, Password hashing (`bcrypt`)            |
| Memory Handling    | Conversational history formatting (like LangChain memory)     |
| Deployment Ready   | Modular code, .env-based configuration                        |
| Frontend Framework | Streamlit for UI/UX                                           |

## Requirements

- Python 3.7 or higher
- Google Generative AI API key
- MongoDB URI (local or hosted on MongoDB Atlas)

## Setup Instructions

1. Clone the Repository

```bash
git clone <repository-url>
```

2. Create Virtual Environment

```bash
conda create -p env python=3.10 -y
```

3. Install Dependencies

```bash
pip install -r requirements.txt
```

4. Environment Configuration Create a .env file in the root directory:

```bash
GOOGLE_API_KEY =your_api_key_here
MONGODB_URI=your_uri_here
```

5. Run the Application

```bash
streamlit run app.py
```

