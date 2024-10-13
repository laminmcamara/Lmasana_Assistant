# Importing necessary libraries
import streamlit as st
import PyPDF2 as pdfReader
import os
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import pipeline
from dotenv import load_dotenv
import io
import mysql.connector

# Load environment variables
load_dotenv()

# Initialize the Hugging Face question-answering pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Function to establish a database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database='healthcare'
    )

# Attempt to connect to the database
try:
    db_connection = get_db_connection()
    st.success("Database connection successful!")
except mysql.connector.Error as err:
    st.error(f"Error connecting to the database: {err}")
    db_connection = None  # Ensure db_connection is defined as None if connection fails

# Function to fetch FAQs from the database
def fetch_faqs(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT Question, Answer FROM faqs")
    faqs = cursor.fetchall()
    cursor.close()
    return faqs

# Function to search for an answer in the database
def search_db_answer(user_question, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT Answer FROM faqs WHERE Question LIKE %s", (f"%{user_question}%",))
    answer = cursor.fetchone()
    cursor.close()
    return answer[0] if answer else None

# Function to log feedback in the database
def log_feedback(connection, patient_id, appointment_id, feedback_text, rating):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO feedback (PatientID, AppointmentID, FeedbackText, Rating, CreatedAt) VALUES (%s, %s, %s, %s, NOW())",
        (patient_id, appointment_id, feedback_text, rating)
    )
    connection.commit()
    cursor.close()

# Function to process uploaded files and extract text
def extract_text_from_files(uploaded_files):
    full_text = ""
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.type == "application/pdf":
                pdf_reader = pdfReader.PdfReader(io.BytesIO(uploaded_file.read()))
                for page in pdf_reader.pages:
                    full_text += page.extract_text() or ""
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(io.BytesIO(uploaded_file.read()))
                for paragraph in doc.paragraphs:
                    full_text += paragraph.text + "\n"
        except Exception as e:
            st.error(f"Error processing file: {e}")
    return full_text

# Improved text chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Adjust chunk size as needed
    chunk_overlap=200  # Add overlap to maintain context
)

# Function to split extracted text into chunks
def split_text_to_chunks(full_text):
    return text_splitter.split_text(full_text)

# Function to generate question suggestions
def generate_suggestions(query=""):
    all_suggestions = [
        "What are the different types of healthcare services?",
        "How can I contact customer support?",
        "What is the process for scheduling an appointment?",
        "Where can I find information on insurance coverage?",
        "What are the hours of operation for the clinic?",
        "Can you explain the patient referral process?",
        "What should I do in case of a medical emergency?"
    ]
    # Filter suggestions based on user input
    return [s for s in all_suggestions if query.lower() in s.lower()]

# Streamlit interface
st.title("Lmasana Assistant: Database Chat and Document Inquiries (PDF, DOCX)")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose an option:", ["Home", "FAQs", "Upload Files"])

# Initialize feedback messages
feedback_message_db = None
feedback_message_content = None

if page == "Home":
    st.header("Welcome to Lmasana Health Care Database Support Assistant")
    st.write("Feel free to ask your questions or upload documents for assistance.")

    # Allow users to ask a question about the database
    user_question_db = st.text_input("Ask your question about our healthcare (Database):", key="db_question")

    # Display suggestions dynamically as the user types
    if user_question_db:
        suggestions = generate_suggestions(user_question_db)
        if suggestions:
            st.subheader("Suggestions for Questions:")
            for suggestion in suggestions:
                st.write(f"- {suggestion}")

    if st.button("Send Database Question"):
        if user_question_db and db_connection:
            db_answer = search_db_answer(user_question_db, db_connection)
            if db_answer:
                st.write("Answer from FAQs:")
                st.write(db_answer)
            else:
                st.warning("No answer found in the database for your question.")
                feedback_message_db = "Suggested Action: Please try rephrasing your question or check our FAQs."
                feedback_message_db += "\nSupport Team Contacts: "
                feedback_message_db += "\n1. Contact us on LinkedIn: [ln/laminmasanacamara]"
                feedback_message_db += "\n2. Call us: +85262144214"
        else:
            st.warning("Please enter a question.")

    # Show feedback message if applicable
    if feedback_message_db:
        st.write(feedback_message_db)

    # Feedback section for database question
    if 'db_answer' in locals() and db_answer is not None:
        feedback_db = st.radio("Was this answer helpful?", ("Yes", "No"), key="feedback_db")
        rating = st.slider("Rate your experience (1-5)", 1, 5, 3)  # Rating slider
        patient_id = st.number_input("Enter your Patient ID:", min_value=1)  # Example input
        appointment_id = st.number_input("Enter your Appointment ID:", min_value=1)  # Example input
        if st.button("Submit Feedback for Database Answer"):
            log_feedback(db_connection, patient_id, appointment_id, feedback_db, rating)  # Log feedback
            feedback_message_db = f"Thank you for your feedback: {feedback_db}!"

elif page == "FAQs":
    if db_connection:
        faqs = fetch_faqs(db_connection)
        if faqs:
            st.header("Frequently Asked Questions")
            for faq in faqs:
                st.subheader(f"Q: {faq['Question']}")
                st.write(f"A: {faq['Answer']}")
        else:
            st.write("No FAQs available at the moment.")
    else:
        st.warning("Database connection is not available.")

# Upload Files page
if page == "Upload Files":
    # Initialize variables for answers
    content_answer = None

    # File uploader for PDF or DOCX files
    uploaded_files = st.file_uploader("Upload your PDF or DOCX files to query", type=["pdf", "docx"], accept_multiple_files=True)
    full_text = ""
    if uploaded_files:
        full_text = extract_text_from_files(uploaded_files)
        st.write("Extracted Text:")
        st.text_area("Extracted Text", full_text, height=300)

        # Split text into manageable chunks
        text_chunks = split_text_to_chunks(full_text) if full_text else []

        # Allow users to ask a question about the content
        question_content = st.text_input("Ask a question about the support content (Uploaded files):")
        if st.button("Send Content Question"):
            if question_content and text_chunks:
                combined_context = " ".join(text_chunks)
                qa_answer = qa_pipeline(question=question_content, context=combined_context)
                content_answer = qa_answer['answer']
                st.write("Answer from uploaded content/PDF:")
                st.write(content_answer)
            else:
                st.warning("Please upload files and ask a question about the content.")

    # Feedback section for content question
    if content_answer is not None:
        feedback_content = st.radio("Was this answer helpful?", ("Yes", "No"), key="feedback_content")
        rating = st.slider("Rate your experience (1-5)", 1, 5, 3)  # Rating slider
        if st.button("Submit Feedback for Content Answer"):
            # Log feedback without PatientID and AppointmentID
            log_feedback(db_connection, None, None, feedback_content, rating)  # Log feedback
            feedback_message_content = f"Thank you for your feedback: {feedback_content}!"

    # Show feedback message if applicable
    if feedback_message_content:
        st.write(feedback_message_content)

    # Handle case where no answer is found in both sources
    if ('db_answer' not in locals() or db_answer is None) and (content_answer is None):
        st.warning("No answer found in either the database or uploaded content.")
        st.write("Suggested Action: Please contact our support team for further assistance.")
        st.write("Support Team Contacts: ")
        st.write("1. Contact us on LinkedIn: [ln/laminmasanacamara]")
        st.write("2. Call us: +85262144214")

# Close the database connection when done
if db_connection:
    db_connection.close()