# **Event Management System**

This project is a Flask-based event management system with a responsive HTML interface and robust user role management. It allows superusers, attendees, and guest users to interact with events and tickets seamlessly.

---

## **Features**

### **Superuser Features**
- Add events with details like name, date, duration (up to 12 hours), capacity, and location.
- Cancel events, notifying all attendees via email.
- Modify event capacity (up to 100,000 users).
- View all events, canceled events, and transaction logs.
- Receive email notifications when an event’s remaining capacity falls below 5%.
- Reset passwords via email or change passwords while logged in.
- Superusers cannot acquire tickets for events.

### **Attendee Features**
- View all events and canceled events.
- Get tickets (up to 5 per event) with email confirmation.
- View tickets, including barcodes for validation.
- Cancel tickets with email confirmations.
- View the remaining number of tickets (when capacity falls below 5%).
- Reset passwords via email or change passwords while logged in.

### **Guest User Features**
- View events and canceled events.
- View remaining tickets for events (when capacity falls below 5%).
- Register an account to become an attendee.

---

## **Setup Instructions**

### **Prerequisites**
Ensure you have the following installed:
- Python 3.7+
- Flask and required dependencies
- SQLite (for `site.db`)
- Email service credentials for password reset functionality

### **Install Dependencies**
Run the following commands to install required packages and set up the environment:
```bash
python3 -m venv vcwk
source vcwk/bin/activate
pip install -r requirements.txt
```

---

## **How to Run**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/event-management-system.git
   cd event-management-system
   ```

2. **Run the Application**:
   Use the provided script:
   ```bash
   bash run.sh
   ```
   The application will start on `http://127.0.0.1:5000`.

3. **Database Initialization**:
   The first registered user becomes the superuser. Subsequent registrations are normal attendees.

4. **Access the Application**:
   Open your browser and navigate to the URL provided in the terminal output.

5. **Clean the Environment**:
   Use `clean.sh` to clean up temporary files and the virtual environment:
   ```bash
   bash clean.sh
   ```

---

## **Frontend Design**
The user interface is built with HTML, CSS, and images, following a purple neon theme. Key features include:
- Responsive navigation via a navbar.
- Homepage with an image carousel showcasing past events.

---

## **Demo**
- The demo video (`demo.mp4`) showcases the system's features. Subtitles are included to explain the functionalities.

---

## **Key Components**

- **Flask Application**:
  - Main app file: `eventbyte.py`
  - Routing and functionality for events and tickets.

- **Database**:
  - SQLite database: `site.db`.

- **Scripts**:
  - `run.sh`: Automates running the Flask application.
  - `clean.sh`: Cleans up virtual environments and temporary files.

- **Frontend**:
  - HTML pages and images provide an interactive user experience.

---

## **Future Enhancements**
- Add dynamic capacity adjustment based on demand.
- Integrate a payment gateway for ticket purchases.
- Include analytics for superusers to monitor attendee trends.

---

## **Acknowledgments**
- Flask for its lightweight yet powerful web framework.
- SQLite for seamless database integration.
- Email services for secure password reset and notifications.

---

