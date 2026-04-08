from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from utils.data_manager import load_data, save_data, get_next_id
from utils.baidu_ai import BaiduRecognizer
from datetime import datetime, timedelta
import collections

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # In production, use a secure key

# Helper to check if logged in
def is_logged_in():
    return 'user_id' in session

def get_current_user():
    if not is_logged_in():
        return None
    users = load_data('users')
    for user in users:
        if user['id'] == session['user_id']:
            return user
    return None

@app.route('/')
def index():
    if is_logged_in():
        user = get_current_user()
        if user['role'] == 'vendor':
            return redirect(url_for('vendor_dashboard'))
        return redirect(url_for('restaurant_list'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role'] # 'customer' or 'vendor'
        
        users = load_data('users')
        if any(u['username'] == username for u in users):
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        new_user = {
            'id': get_next_id(users),
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': role
        }
        users.append(new_user)
        save_data('users', users)
        
        # If vendor, create a restaurant placeholder
        if role == 'vendor':
            restaurants = load_data('restaurants')
            new_restaurant = {
                'id': get_next_id(restaurants),
                'owner_id': new_user['id'],
                'name': f"{username}'s Restaurant",
                'description': "Delicious food served here.",
                'image': "https://via.placeholder.com/300"
            }
            restaurants.append(new_restaurant)
            save_data('restaurants', restaurants)
            
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_data('users')
        user = next((u for u in users if u['username'] == username), None)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']
            flash('Login successful.', 'success')
            if user['role'] == 'vendor':
                return redirect(url_for('vendor_dashboard'))
            return redirect(url_for('restaurant_list'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# --- VENDOR ROUTES ---

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if not is_logged_in() or session['role'] != 'vendor':
        return redirect(url_for('login'))
    
    # Get vendor's restaurant
    restaurants = load_data('restaurants')
    my_restaurant = next((r for r in restaurants if r['owner_id'] == session['user_id']), None)
    
    # Get orders for this restaurant
    orders = load_data('orders')
    my_orders = [o for o in orders if o['restaurant_id'] == my_restaurant['id']] if my_restaurant else []
    
    # Calculate stats
    total_orders = len(my_orders)
    pending_orders = len([o for o in my_orders if o['status'] == 'Pending'])
    
    # 1. Daily Revenue (Last 7 days)
    today = datetime.now().date()
    dates = []
    revenues = []
    
    # Initialize dictionary for last 7 days
    revenue_map = {}
    for i in range(6, -1, -1):
        date_obj = today - timedelta(days=i)
        date_str = date_obj.strftime("%Y-%m-%d")
        dates.append(date_str)
        revenue_map[date_str] = 0.0
        
    for order in my_orders:
        # Assuming order['created_at'] is "YYYY-MM-DD HH:MM:SS"
        try:
            order_date = datetime.strptime(order['created_at'], "%Y-%m-%d %H:%M:%S").date().strftime("%Y-%m-%d")
            if order_date in revenue_map:
                revenue_map[order_date] += order['total_price']
        except ValueError:
            pass # Skip invalid dates
            
    revenues = [revenue_map[d] for d in dates]
    
    # 2. Order Status Distribution
    status_counts = collections.defaultdict(int)
    for order in my_orders:
        status_counts[order['status']] += 1
    
    # Ensure specific order of statuses for chart
    status_labels = ['Pending', 'Accepted', 'Preparing', 'Delivering', 'Completed', 'Rejected']
    status_data = [status_counts[s] for s in status_labels]
    
    # 3. Top Selling Items
    item_sales = collections.defaultdict(int)
    for order in my_orders:
        if order['status'] != 'Rejected': # Only count valid orders
            for item in order['items']:
                item_sales[item['name']] += item['quantity']
    
    # Get top 5
    top_items_list = sorted(item_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    top_items_labels = [x[0] for x in top_items_list]
    top_items_data = [x[1] for x in top_items_list]

    return render_template('vendor_dashboard.html', 
                           restaurant=my_restaurant, 
                           total_orders=total_orders, 
                           pending_orders=pending_orders,
                           dates=dates,
                           revenues=revenues,
                           status_labels=status_labels,
                           status_data=status_data,
                           top_items_labels=top_items_labels,
                           top_items_data=top_items_data)

@app.route('/api/recognize_food', methods=['POST'])
def recognize_food():
    if 'image' not in request.files:
        return {'error': 'No image file provided'}, 400
    
    file = request.files['image']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
        
    if file:
        image_data = file.read()
        recognizer = BaiduRecognizer()
        results = recognizer.recognize_ingredient(image_data)
        
        if results:
            # Return top result
            top_result = results[0]
            return {
                'name': top_result['name'],
                'score': top_result['score'],
                'all_results': results # Send all for potential dropdown selection
            }
        else:
            return {'error': 'Recognition failed'}, 500

@app.route('/vendor/menu', methods=['GET', 'POST'])
def manage_menu():
    if not is_logged_in() or session['role'] != 'vendor':
        return redirect(url_for('login'))
        
    restaurants = load_data('restaurants')
    my_restaurant = next((r for r in restaurants if r['owner_id'] == session['user_id']), None)
    if not my_restaurant:
        flash("Restaurant not found for this vendor.", "danger")
        return redirect(url_for('vendor_dashboard'))

    menu_items = load_data('menu_items')
    my_menu = [m for m in menu_items if m['restaurant_id'] == my_restaurant['id']]
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            new_item = {
                'id': get_next_id(menu_items),
                'restaurant_id': my_restaurant['id'],
                'name': request.form['name'],
                'description': request.form['description'],
                'price': float(request.form['price']),
                'image': request.form.get('image', 'https://via.placeholder.com/150')
            }
            menu_items.append(new_item)
            save_data('menu_items', menu_items)
            flash('Menu item added successfully', 'success')
            
        elif action == 'edit':
            item_id = int(request.form['item_id'])
            for item in menu_items:
                if item['id'] == item_id and item['restaurant_id'] == my_restaurant['id']:
                    item['name'] = request.form['name']
                    item['description'] = request.form['description']
                    item['price'] = float(request.form['price'])
                    break
            save_data('menu_items', menu_items)
            flash('Menu item updated successfully', 'success')
            
        elif action == 'delete':
            item_id = int(request.form['item_id'])
            menu_items = [m for m in menu_items if not (m['id'] == item_id and m['restaurant_id'] == my_restaurant['id'])]
            save_data('menu_items', menu_items)
            flash('Menu item deleted successfully', 'success')
            
        return redirect(url_for('manage_menu'))

    return render_template('manage_menu.html', menu=my_menu)

@app.route('/vendor/orders', methods=['GET', 'POST'])
def vendor_orders():
    if not is_logged_in() or session['role'] != 'vendor':
        return redirect(url_for('login'))
        
    restaurants = load_data('restaurants')
    my_restaurant = next((r for r in restaurants if r['owner_id'] == session['user_id']), None)
    
    orders = load_data('orders')
    my_orders = [o for o in orders if o['restaurant_id'] == my_restaurant['id']]
    
    # Sort orders by date descending
    my_orders.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Enhance order data with customer names
    users = load_data('users')
    user_map = {u['id']: u['username'] for u in users}
    
    for order in my_orders:
        order['username'] = user_map.get(order['user_id'], 'Unknown User')

    if request.method == 'POST':
        order_id = int(request.form['order_id'])
        new_status = request.form['status']
        
        for order in orders:
            if order['id'] == order_id:
                order['status'] = new_status
                break
        save_data('orders', orders)
        flash(f'Order #{order_id} status updated to {new_status}', 'success')
        return redirect(url_for('vendor_orders'))
        
    return render_template('vendor_orders.html', orders=my_orders)

# --- CUSTOMER ROUTES ---

@app.route('/restaurants')
def restaurant_list():
    restaurants = load_data('restaurants')
    return render_template('restaurant_list.html', restaurants=restaurants)

@app.route('/restaurant/<int:restaurant_id>')
def view_menu(restaurant_id):
    restaurants = load_data('restaurants')
    restaurant = next((r for r in restaurants if r['id'] == restaurant_id), None)
    
    if not restaurant:
        flash('Restaurant not found', 'danger')
        return redirect(url_for('restaurant_list'))
        
    menu_items = load_data('menu_items')
    restaurant_menu = [m for m in menu_items if m['restaurant_id'] == restaurant_id]
    
    return render_template('menu.html', restaurant=restaurant, menu=restaurant_menu)

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []
    
    item_id = int(request.form['item_id'])
    restaurant_id = int(request.form['restaurant_id'])
    quantity = int(request.form.get('quantity', 1))
    
    # Check if cart has items from another restaurant
    if session['cart'] and session['cart'][0]['restaurant_id'] != restaurant_id:
        # Clear cart or warn user? Let's clear for simplicity or append if we support multi-restaurant orders (usually not simple).
        # Standard approach: only one restaurant per order.
        session['cart'] = []
    
    # Check if item already in cart
    found = False
    cart = session['cart']
    for item in cart:
        if item['item_id'] == item_id:
            item['quantity'] += quantity
            found = True
            break
            
    if not found:
        # Need to fetch item details to store name/price in cart for display
        menu_items = load_data('menu_items')
        menu_item = next((m for m in menu_items if m['id'] == item_id), None)
        if menu_item:
            cart.append({
                'item_id': item_id,
                'restaurant_id': restaurant_id,
                'name': menu_item['name'],
                'price': menu_item['price'],
                'quantity': quantity
            })
    
    session['cart'] = cart # Save back to session
    flash('Added to cart', 'success')
    return redirect(url_for('view_menu', restaurant_id=restaurant_id))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/cart/update', methods=['POST'])
def update_cart():
    action = request.form.get('action')
    item_id = int(request.form['item_id'])
    cart = session.get('cart', [])
    
    if action == 'remove':
        cart = [item for item in cart if item['item_id'] != item_id]
    elif action == 'update':
        qty = int(request.form['quantity'])
        for item in cart:
            if item['item_id'] == item_id:
                item['quantity'] = qty
                break
                
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if not is_logged_in():
        flash('Please login to checkout', 'warning')
        return redirect(url_for('login'))
        
    cart = session.get('cart', [])
    if not cart:
        flash('Cart is empty', 'warning')
        return redirect(url_for('restaurant_list'))
        
    orders = load_data('orders')
    
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    restaurant_id = cart[0]['restaurant_id']
    
    new_order = {
        'id': get_next_id(orders),
        'user_id': session['user_id'],
        'restaurant_id': restaurant_id,
        'items': cart,
        'total_price': total_price,
        'status': 'Pending',
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    orders.append(new_order)
    save_data('orders', orders)
    
    session.pop('cart', None)
    flash('Order placed successfully!', 'success')
    return redirect(url_for('order_history'))

@app.route('/orders')
def order_history():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    orders = load_data('orders')
    my_orders = [o for o in orders if o['user_id'] == session['user_id']]
    my_orders.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Enhance order data with restaurant names
    restaurants = load_data('restaurants')
    rest_map = {r['id']: r['name'] for r in restaurants}
    
    for order in my_orders:
        order['restaurant_name'] = rest_map.get(order['restaurant_id'], 'Unknown Restaurant')
        
    return render_template('order_history.html', orders=my_orders)

@app.route('/order/<int:order_id>')
def order_detail(order_id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    orders = load_data('orders')
    order = next((o for o in orders if o['id'] == order_id), None)
    
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('order_history'))
        
    # Check permissions (user owns order OR vendor owns restaurant)
    is_owner = order['user_id'] == session['user_id']
    
    restaurants = load_data('restaurants')
    restaurant = next((r for r in restaurants if r['id'] == order['restaurant_id']), None)
    is_vendor = restaurant and restaurant['owner_id'] == session['user_id']
    
    if not (is_owner or is_vendor):
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
        
    return render_template('order_detail.html', order=order, restaurant=restaurant)

if __name__ == '__main__':
    app.run(debug=True)
