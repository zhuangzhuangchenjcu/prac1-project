# FeedMe - Food Delivery Platform

FeedMe is a simplified food delivery web application built with Python (Flask). It allows customers to browse restaurants, view menus, and place orders, while vendors can manage their menus and orders.

## Features

### Customer Side
- **Browse Restaurants**: View a list of available restaurants.
- **View Menu**: See item details and prices.
- **Shopping Cart**: Add items, update quantities, and remove items.
- **Checkout**: Mock payment and order submission.
- **Order History**: View past orders and their real-time status.

### Vendor Side
- **Dashboard**: Overview of restaurant operations (total orders, pending orders, revenue charts).
- **Menu Management**: Add, edit, and delete menu items (with Baidu AI integration for ingredient recognition).
- **Order Management**: Process orders through a complete workflow:
  - Pending -> Accepted -> Preparing -> Delivering -> Completed
  - (Or Reject orders if necessary)

## Tech Stack
- **Backend**: Python (Flask)
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)
- **Database**: Local JSON files (No MySQL required)
- **AI Integration**: Baidu Image Recognition API (for menu items)

## Installation Guide

1. **Enter Project Directory**:
   ```bash
   cd feedme
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   python app.py
   ```

4. **Access Application**:
   Open browser and visit `http://127.0.0.1:5000`

## Project Structure

```
feedme/
├── app.py              # Main application entry point
├── data/               # JSON data storage
│   ├── users.json
│   ├── restaurants.json
│   ├── menu_items.json
│   └── orders.json
├── static/             # Static assets (CSS, JS)
├── templates/          # HTML templates
└── utils/              # Helper functions
```

## Data Model (JSON)

- **Users**: Stores customer and vendor accounts.
- **Restaurants**: Stores restaurant details (linked to vendors).
- **Menu Items**: Stores food items (linked to restaurants).
- **Orders**: Stores order details, items, and status.

## License
MIT

## Test Accounts
For testing purposes, the system comes with the following accounts (password is `password123`):

### Vendor Accounts
- `vendor_chinese` (Beijing Noodles)
- `vendor_pizza` (Pizza House)
- `vendor_dessert` (Sweet Desserts)

### Customer Accounts
- `customer1`
- `customer2`
- `customer3`
