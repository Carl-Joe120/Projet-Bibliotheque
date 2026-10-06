# Bibliothèque Michel Tardieu — Library Management System

A web-based library management system developed with **Python and Django** to digitize and simplify the management of books, users, reservations, loans, returns, penalties, notifications, and library operations.

This project was developed as part of a Computer Science license project and focuses on building a centralized, database-driven solution for managing library resources and daily activities.

---

##  About the Project

**Bibliothèque Michel Tardieu** is a Django-based web application designed to centralize the main operations of a library.

The system provides role-based access to different users and supports book management, inventory tracking, reservations, loans, returns, penalties, notifications, dashboards, and QR-code based reservation validation.

The application uses **MySQL** as its relational database and follows a modular Django architecture with multiple applications dedicated to specific business functionalities.

---

##  Main Features

###  User Management

* User authentication and login
* Role-based access control
* Management of different user roles
* Member, secretary, employee, and administrator functionalities

###  Book & Inventory Management

* Book registration and management
* Book inventory management
* Stock tracking
* Book availability management

###  Loan & Return Management

* Book borrowing
* Return processing
* Loan tracking
* Overdue management
* Penalty management

###  Reservation Management

* Online and physical reservation management
* Reservation status tracking
* Reservation expiration
* Reservation validation
* QR-code based reservation workflow

###  Reservation Validation & QR Code Workflow

When a member submits a reservation, the system first checks the business rules and eligibility conditions.

Examples of checks include:

* Existing overdue books
* Number of books currently borrowed and not yet returned
* Other reservation constraints defined by the library rules

When all required conditions are satisfied:

1. The reservation is processed successfully.
2. **Django Signals** trigger the notification workflow.
3. The member receives an **in-app notification**.
4. The notification provides the possibility to **download the QR code** associated with the reservation.
5. The QR code contains information related to the reservation.
6. The member also receives the QR code by **email**.
7. The QR code can then be scanned for reservation validation.

For local testing, the device used to scan the QR code must be connected to the **same local network (Wi-Fi or hotspot)** as the computer running the Django application.

###  Notifications

* In-app notifications
* Email notifications
* Reservation-related notifications
* Overdue notifications
* Dashboard alerts

###  Dashboard & Data Visualization

* Administrative dashboard
* Library statistics
* Activity monitoring
* Data visualization
* Information for monitoring library operations

###  Recommendation System

* Book recommendation functionality
* Personalized recommendation features based on the application's logic

---

##  Technologies Used

### Backend

* **Python**
* **Django**
* **Django ORM**
* **Django Signals**

### Database

* **MySQL**

### Frontend

* **HTML5**
* **CSS3**
* **Bootstrap**
* **JavaScript**

### Other Technologies

* **QR Code**
* **Pillow**
* **Email / SMTP**
* Django authentication and authorization

---

##  Project Structure

The application is organized into several Django applications:

| Application            | Purpose                                     |
| ---------------------- | ------------------------------------------- |
| `utilisateurs`         | User management and authentication          |
| `livres`               | Book and inventory management               |
| `reservation`          | Reservation management and QR-code workflow |
| `employes`             | Employee-related functionalities            |
| `notifications`        | In-app notifications and alerts             |
| `recommandations`      | Book recommendation functionality           |
| `tableau_de_bord`      | Dashboard and statistics                    |
| `bibliotheque_Project` | Main Django project configuration           |

This modular structure separates the main business functionalities of the system and facilitates maintenance and future extensions.

---

##  User Roles

The system includes different roles with specific responsibilities and permissions:

###  Member

* Browse available books
* Make reservations
* Follow reservations
* Receive notifications
* Receive and use reservation QR codes

###  Secretary

* Manage reservations
* Validate reservations
* Handle library operations related to members

###  Employee

* Perform operational library tasks
* Manage assigned library activities

###  Administrator

* Manage users and system administration
* Access administrative functionalities
* Monitor the application

---

##  Installation & Setup

### Prerequisites

Make sure you have installed:

* Python
* MySQL
* Git

### 1. Clone the repository

```bash
git clone https://github.com/Carl-Joe120/Projet-Bibliotheque.git
cd Projet-Bibliotheque
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

The project includes a `requirements.txt` file containing the required Python packages.

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

Create a MySQL database named:

```text
bibliotheque
```

Then configure your local database credentials in the Django settings.

> **Security note:** Never commit database passwords, email passwords, Django secret keys, or other credentials to a public repository.

### 5. Apply migrations


### 6. Create a superuser


### 7. Run the development server

```bash
python manage.py runserver 0.0.0.0:8000
```

Then open the application from the browser:

```text
http://127.0.0.1:8000/
```

For access from another device on the same local network, use the computer's local IP address:

```text
http://YOUR_LOCAL_IP:8000/
```

---

##  QR Code Testing on a Local Network

To test the QR-code workflow using another device:

1. Start the Django server:

```bash
python manage.py runserver 0.0.0.0:8000
```

2. Connect the scanning device to the same Wi-Fi or hotspot as the computer running the server.
3. Use the computer's local IP address to access the application from the other device.
4. Generate a reservation QR code from the member account.
5. Scan the QR code using the authorized validation workflow.

---

##  Screenshots

Screenshots of the main application interfaces will be added here.

### Login

# 📚 Bibliothèque Michel Tardieu — Library Management System

A web-based library management system developed with **Python and Django** to digitize and simplify the management of books, users, reservations, loans, returns, penalties, notifications, and library operations.

This project was developed as part of a Computer Science license project and focuses on building a centralized, database-driven solution for managing library resources and daily activities.

---

##  About the Project

**Bibliothèque Michel Tardieu** is a Django-based web application designed to centralize the main operations of a library.

The system provides role-based access to different users and supports book management, inventory tracking, reservations, loans, returns, penalties, notifications, dashboards, and QR-code based reservation validation.

The application uses **MySQL** as its relational database and follows a modular Django architecture with multiple applications dedicated to specific business functionalities.

---

##  Main Features

###  User Management

* User authentication and login
* Role-based access control
* Management of different user roles
* Member, secretary, employee, and administrator functionalities

###  Book & Inventory Management

* Book registration and management
* Book inventory management
* Stock tracking
* Book availability management

###  Loan & Return Management

* Book borrowing
* Return processing
* Loan tracking
* Overdue management
* Penalty management

###  Reservation Management

* Online and physical reservation management
* Reservation status tracking
* Reservation expiration
* Reservation validation
* QR-code based reservation workflow

###  Reservation Validation & QR Code Workflow

When a member submits a reservation, the system first checks the business rules and eligibility conditions.

Examples of checks include:

* Existing overdue books
* Number of books currently borrowed and not yet returned
* Other reservation constraints defined by the library rules

When all required conditions are satisfied:

1. The reservation is processed successfully.
2. **Django Signals** trigger the notification workflow.
3. The member receives an **in-app notification**.
4. The notification provides the possibility to **download the QR code** associated with the reservation.
5. The QR code contains information related to the reservation.
6. The member also receives the QR code by **email**.
7. The QR code can then be scanned for reservation validation.

For local testing, the device used to scan the QR code must be connected to the **same local network (Wi-Fi or hotspot)** as the computer running the Django application.

###  Notifications

* In-app notifications
* Email notifications
* Reservation-related notifications
* Overdue notifications
* Dashboard alerts

###  Dashboard & Data Visualization

* Administrative dashboard
* Library statistics
* Activity monitoring
* Data visualization
* Information for monitoring library operations

###  Recommendation System

* Book recommendation functionality
* Personalized recommendation features based on the application's logic

---

##  Technologies Used

### Backend

* **Python**
* **Django**
* **Django ORM**
* **Django Signals**

### Database

* **MySQL**

### Frontend

* **HTML5**
* **CSS3**
* **Bootstrap**
* **JavaScript**

### Other Technologies

* **QR Code**
* **Pillow**
* **Email / SMTP**
* Django authentication and authorization

---

##  Project Structure

The application is organized into several Django applications:

| Application            | Purpose                                     |
| ---------------------- | ------------------------------------------- |
| `utilisateurs`         | User management and authentication          |
| `livres`               | Book and inventory management               |
| `reservation`          | Reservation management and QR-code workflow |
| `employes`             | Employee-related functionalities            |
| `notifications`        | In-app notifications and alerts             |
| `recommandations`      | Book recommendation functionality           |
| `tableau_de_bord`      | Dashboard and statistics                    |
| `bibliotheque_Project` | Main Django project configuration           |

This modular structure separates the main business functionalities of the system and facilitates maintenance and future extensions.

---

##  User Roles

The system includes different roles with specific responsibilities and permissions:

###  Member

* Browse available books
* Make reservations
* Follow reservations
* Receive notifications
* Receive and use reservation QR codes

###  Secretary

* Manage reservations
* Validate reservations
* Handle library operations related to members

###  Employee

* Perform operational library tasks
* Manage assigned library activities

###  Administrator

* Manage users and system administration
* Access administrative functionalities
* Monitor the application

---

##  Installation & Setup

### Prerequisites

Make sure you have installed:

* Python
* MySQL
* Git

```

### 2. Create a virtual environment


Activate it on Windows:
or
On macOS/Linux:
```

### 3. Install dependencies



### 4. Configure MySQL

Create a MySQL database named:

```

Then configure your local database credentials in the Django settings.


### 5. Apply migrations


### 6. Create a superuser

### 7. Run the development server


Then open the application from the browser:

```text
http://127.0.0.1:8000/
```

For access from another device on the same local network, use the computer's local IP address:

```text
http://YOUR_LOCAL_IP:8000/
```

---

##  QR Code Testing on a Local Network

To test the QR-code workflow using another device:

1. Start the Django server:

```bash
python manage.py runserver 0.0.0.0:8000
```

2. Connect the scanning device to the same Wi-Fi or hotspot as the computer running the server.
3. Use the computer's local IP address to access the application from the other device.
4. Generate a reservation QR code from the member account.
5. Scan the QR code using the authorized validation workflow.

---

##  Screenshots

Screenshots of the main application interfaces will be added here.

### Login
 
https://github.com/Carl-Joe120/Projet-Bibliotheque/Login.png
### Member Dashboard

 
### Book Management

 


### Reservation
 


### QR Code

 

### QR Code Validation

 
 


### Notifications

 
### Secretary Dashboard

 

### Reservation management by Secretary
 

### Book landing management by secretary
 

### Returning Borrowing books 
 








### Books listing management by secretary
 

### Books adding section by secretary
 




### Late returning Books section management by secretary
 

### Members management by secretary
 





Analysis and Report section By Secretary
 

 

### Secretary profile section
 

### Super Admin Dashboard
 







### Members Management by superadmin
 

### Secretary Management by Superadmin
 







### Books Management by Superadmin
 

###Statistics section for Superadmin
 

### Logs system Management for superadmin
 

### Permissions section for superadmin
 
## 🎯 Project Objectives

The project aims to:

* Digitize library management processes
* Centralize library data and operations
* Improve book and inventory tracking
* Simplify reservations, loans, and returns
* Automate notifications
* Improve reservation validation through QR codes
* Provide dashboards and statistics for monitoring library activities
* Improve the organization and traceability of library operations

---

## 🔮 Future Improvements

Possible future improvements include:

* Deployment to a production server
* Cloud database integration
* Advanced analytics and reporting
* Improved recommendation algorithms
* Mobile application integration
* Additional notification channels
* Enhanced automated testing

---

## 👨‍💻 Author

**Carl Jessy Bazile**

Computer Science | Python & Django | Data Engineering | SQL & Databases

Interested in backend development, database systems, software development, and data engineering.


## 🎯 Project Objectives

The project aims to:

* Digitize library management processes
* Centralize library data and operations
* Improve book and inventory tracking
* Simplify reservations, loans, and returns
* Automate notifications
* Improve reservation validation through QR codes
* Provide dashboards and statistics for monitoring library activities
* Improve the organization and traceability of library operations

---

## 🔮 Future Improvements

Possible future improvements include:

* Deployment to a production server
* Cloud database integration
* Advanced analytics and reporting
* Improved recommendation algorithms
* Mobile application integration
* Additional notification channels
* Enhanced automated testing

---

## 👨‍💻 Author

**Carl Jessy Bazile**

Computer Science | Python & Django | Data Engineering | SQL & Databases

Interested in backend development, database systems, software development, and data engineering.
