# Legends Restaurant

Legends Restaurant is a web-based takeaway and delivery management system developed as a university software engineering project. The system helps customers browse the menu, place orders, and track order status, while also allowing staff and managers to manage restaurant operations through dedicated dashboards.

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
