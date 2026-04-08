# FeedMe - Testing Guide

## Manual Testing Steps

### 1. Registration & Login
- [ ] Open `http://127.0.0.1:5000`
- [ ] Click **Register**
- [ ] Create a **Customer** account (e.g., `cust1`/`pass1`)
- [ ] Create a **Vendor** account (e.g., `vend1`/`pass1`)
- [ ] Login as `cust1` -> Redirects to Restaurant List
- [ ] Login as `vend1` -> Redirects to Vendor Dashboard

### 2. Vendor Management
- [ ] Login as `vend1`
- [ ] Go to **My Menu**
- [ ] Add a new item: "Burger", "Juicy beef burger", "10.50"
- [ ] Verify item appears in list
- [ ] Edit item: Change price to "11.00"
- [ ] Delete item (optional)
- [ ] Check **Dashboard** for empty stats

### 3. Customer Ordering
- [ ] Login as `cust1`
- [ ] Go to **Restaurants** -> Should see "vend1's Restaurant"
- [ ] Click **View Menu** -> Should see "Burger" for $11.00
- [ ] Add 2 Burgers to cart
- [ ] Go to **Cart** -> Verify total is $22.00
- [ ] Update quantity to 1 -> Verify total is $11.00
- [ ] Click **Checkout** -> "Order placed successfully!"
- [ ] Go to **My Orders** -> Verify order #1 status is "Pending"

### 4. Order Processing (Vendor)
- [ ] Login as `vend1`
- [ ] Check **Dashboard** -> Pending Orders should be 1
- [ ] Go to **Orders** -> Verify order #1 details
- [ ] Click **Accept** -> Status changes to "Accepted"
- [ ] Click **Complete** -> Status changes to "Completed"

### 5. Order Verification (Customer)
- [ ] Login as `cust1`
- [ ] Go to **My Orders** -> Verify order #1 status is "Completed"
