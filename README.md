Lmasana Assistant
Overview:

Lmasana Assistant is a healthcare support application built with Streamlit. It enables users to query a database of frequently asked questions (FAQs) and upload documents (PDF, DOCX) to obtain answers. The application leverages advanced question-answering models to provide accurate and contextually relevant responses.

Features:
Healthcare Queries: Ask questions related to healthcare services and receive answers from a database. Document Upload: Upload PDF and DOCX files for content-based question answering. Dynamic Suggestions: Get suggestions for common questions as users type. Feedback Mechanism: Users can rate the helpfulness of answers.

Technologies Used:
Python:
Primary programming language (3.12 or higher).

Streamlit:
Framework for developing the web application.

Transformers:
Hugging Face models for question answering (DistilBERT and T5).

MySQL:
Database for storing FAQs and feedback.

mysql-connector-python:
Connector for MySQL database.
dotenv:
For managing environment variables.
Installation
Prerequisites Python 3.12 MySQL Server MySQL Connector for Python

Steps
Clone the repository:
git clone https://github.com/laminmcamara/lmasana_assistant.git cd lmasana_assistant

Install the required packages:
pip install -r requirements.txt

Ensure you have the MySQL Connector installed:
pip install mysql-connector-python

Set up your MySQL database:
Create a database named 'healthcare'.

Create the necessary tables (faqs, feedback, etc.) as defined in the code.

Create a .env file in the project root with the following content: DB_HOST=your_database_host DB_USER=your_database_user DB_PASSWORD=your_database_password

Create a virtual environment: python -m venv venv

Activate the virtual environment:

On Windows: venv\Scripts\activate On macOS/Linux: source venv/bin/activate

Usage
To run the application, execute the following command: streamlit run app.py

Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for discussion.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
For any inquiries, please contact:

Lamin M Camara: laminmasana@gmail.com LinkedIn: laminmasanacamara


