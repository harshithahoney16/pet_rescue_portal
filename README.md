# 🐾 PetSphere – Pet Adoption and Rescue Management Portal

PetSphere is a Django-based web application developed to simplify pet adoption, lost pet reporting, and found pet management. The platform provides a centralized system for users and administrators to manage pet-related reports and requests.

## 🚀 Features

- User Registration and Login
- User Profile Management
- Report Lost Pets
- Report Found Pets
- Pet Adoption Requests
- Pet Status Tracking
- Admin Dashboard
- Approve or Reject Pet Reports
- Manage Lost and Found Requests
- Manage Registered Users
- Pending Task Management
- Image Upload for Pet Reports

## 🛠️ Technologies Used

- Python
- Django
- SQLite
- HTML
- CSS
- Tailwind CSS
- JavaScript
- Chart.js

## 📁 Project Structure

    petproject/
    ├── media/
    ├── petapp/
    ├── petappcore/
    ├── pets/
    ├── manage.py
    └── db.sqlite3

## ⚙️ Installation and Setup

1. Clone the repository

        git clone https://github.com/harshithahoney16/pet_rescue_portal.git

2. Navigate to the project folder

       cd petproject

3. Create a virtual environment

       python -m venv venv

4. Activate the virtual environment

   Windows:

       venv\Scripts\activate

5. Install required dependencies

       pip install -r requirements.txt

6. Apply database migrations

       python manage.py migrate

7. Run the development server

       python manage.py runserver

8. Open the application at:

       http://127.0.0.1:8000/

## 🔐 Environment Variables

Create a `.env` file in the root project directory and configure the required environment variables.

Do not upload the `.env` file to a public repository.

## 🎯 Project Objective

The main objective of PetSphere is to provide an easy-to-use platform for reporting lost and found pets and managing pet adoption requests. It helps connect pet owners, adopters, and administrators through a centralized web application.

## 👩‍💻 Developer

**Harshitha Kanithi**

GitHub: https://github.com/harshithahoney16

B.Tech Computer Science and Engineering

## 📄 License

This project is developed for educational purposes.
