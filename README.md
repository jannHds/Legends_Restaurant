# Legends Restaurant  
### Takeaway & Delivery System

Legends Restaurant is a web-based restaurant ordering and management system developed as a **final course project** for the **Software Engineering course (CSC 305)**.

The system allows customers to browse menu items, place takeaway or delivery orders, and track their order status. Staff members manage order processing, while managers control menu items and system operations through administrative dashboards.

---

## Course Information

**Course:** CSC 305 – Software Engineering  
**Term:** Term 1  
**Academic Year:** 2025 / 2026  
**Course Coordinator:** Dr. Rahma Ahmed  

This project was developed as a required course project following the course guidelines and documentation standards.

---

## Project Title

**Legends Restaurant – Takeaway and Delivery System**

---

## Team Members

Group 1

| Name |
|-----|
| Jana Hassan Algarni | 
| Leen Abdulrahman Hadari | 
| Asma Abbas Albeshri | 
| Lujain Abdullah Alqahtani | 
| Najaf Abdulaziz Al-Mohsen | 
| Shahad Saeed Al-Shahrani | 

---

## Project Overview

This project was built to simulate a real restaurant ordering environment with three main user roles:

- **Customer**: Browse menu items, sign up, log in, manage account, add items to cart, place orders, and track order history.
- **Staff**: View incoming orders and update order statuses.
- **Manager**: Manage users, monitor reports, and control menu items including availability, editing, and deletion.

## Main Features

### Customer Features
- User registration and login
- Browse restaurant menu
- Filter menu by category
- Add items to cart
- Update or remove cart items
- Checkout and payment flow
- View previous orders and order status
- Edit customer account information

### Staff Features
- Staff dashboard for viewing orders
- Update order status:
  - Pending
  - Preparing
  - Out for Delivery
  - Delivered
  - Cancelled

### Manager Features
- Manager dashboard
- Manage users
- Add new users
- Edit existing users
- Manage menu items
- Add, edit, delete, and toggle menu availability
- View reports

## System Roles

The system supports three user roles:

- `customer`
- `staff`
- `manager`

A custom user model is used to support role-based access and store additional details such as phone number, address.

## Technologies Used

- **Python**
- **Django**
- **HTML**
- **CSS**
- **JavaScript**
- **SQLite3**

## Project Structure

```bash
Legends_Restaurant/
│
├── DB/
├── legends/               # Django project settings
├── restaurant/            # Main application
├── media/                 # Uploaded menu images
├── db.sqlite3             # Local database
├── manage.py
└── .gitignore
