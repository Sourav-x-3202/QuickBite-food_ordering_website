from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import uuid
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.secret_key = "quickbite_secret_key"

# File paths
BASE_DIR = "C:/Users/Admin/mannu/bitefood1"
MENU_FILE = os.path.join(BASE_DIR, "data/menu_admin.json")
ORDERS_FILE = os.path.join(BASE_DIR, "data/orders.json")
ADMIN_FILE = os.path.join(BASE_DIR, "data/admins.json")
USERS_FILE = os.path.join(BASE_DIR, "data/users.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")
LOGO_FOLDER = os.path.join(BASE_DIR, "static/logos")

# Ensure required directories exist
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOGO_FOLDER, exist_ok=True)

# JSON helpers
def load_json(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Admin helpers
def load_admins():
    return load_json(ADMIN_FILE)

def save_admins(admins_list):
    save_json(ADMIN_FILE, admins_list)

# User helpers
def load_users():
    return load_json(USERS_FILE)

def save_users(users_list):
    save_json(USERS_FILE, users_list)

# Cart helpers
def get_cart():
    return session.get("cart", [])

def set_cart(cart):
    session["cart"] = cart

def calculate_cart(cart):
    for item in cart:
        item["total"] = item["price"] * item["quantity"]
    total = sum(item["total"] for item in cart)
    return cart, total

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/menu")
def show_menu():
    menu = load_json(MENU_FILE)
    cart_count = sum(item["quantity"] for item in get_cart())
    return render_template("menu.html", menu=menu, cart_count=cart_count)

from flask import jsonify, url_for  # Ensure these are imported

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    item_id = request.form['item_id']  # use as string now
    quantity = int(request.form.get('quantity', 1))

    menu_items = load_json(MENU_FILE)
    item = next((i for i in menu_items if i['id'] == item_id), None)
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    cart = session.get('cart', [])

    for cart_item in cart:
        if cart_item['id'] == item_id:
            cart_item['quantity'] += quantity
            break
    else:
        cart.append({
            'id': item['id'],
            'name': item['name'],
            'price': item['price'],
            'restaurant': item.get('restaurant_name', ''),
            'image': url_for('static', filename=f'uploads/{item["image"]}')
,
            'quantity': quantity
        })

    session['cart'] = cart
    session.modified = True

    return jsonify({'success': True, 'cart_count': sum(i['quantity'] for i in cart)})


@app.route('/order-now', methods=['POST'])
def order_now():
    item_id = request.form['item_id']  # UUID, keep as string
    restaurant_name = request.form['restaurant_name']
    quantity = int(request.form.get('quantity', 1))

    menu = load_json(MENU_FILE)
    item = next((i for i in menu if i['id'] == item_id), None)

    if not item:
        return "Item not found", 404

    cart_item = {
        "name": item["name"],
        "price": item["price"],
        "quantity": quantity,
        "restaurant_name": restaurant_name,
        "image": item.get("image", "")
    }

    cart = session.get("cart", [])
    cart.append(cart_item)
    session["cart"] = cart

    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    cart = get_cart()
    cart, total = calculate_cart(cart)
    return render_template("cart.html", cart_items=cart, total=total, cart_count=sum(i["quantity"] for i in cart))

@app.route("/remove/<int:item_index>")
def remove_item(item_index):
    cart = get_cart()
    if 0 <= item_index < len(cart):
        cart.pop(item_index)
        set_cart(cart)
    return redirect(url_for("cart"))

@app.route("/clear-cart")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("cart"))

@app.route("/place-order", methods=["POST"])
def place_order():
    cart = get_cart()
    if not cart:
        flash("Your cart is empty.")
        return redirect(url_for("show_menu"))

    cart, total = calculate_cart(cart)

    orders = load_json(ORDERS_FILE)
    order = {
        "items": cart,
        "total": total
    }
    orders.append(order)
    save_json(ORDERS_FILE, orders)

    session.pop("cart", None)
    flash("Order placed successfully!")
    return redirect(url_for("show_menu"))

@app.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        for user in users:
            if user["username"] == username and check_password_hash(user["password"], password):
                session["user"] = username
                return redirect(url_for("show_menu"))
        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            return render_template("register.html", error="Passwords do not match")

        users = load_users()
        if any(user["username"] == username for user in users):
            return render_template("register.html", error="Username already exists")

        hashed_password = generate_password_hash(password)
        users.append({"username": username, "password": hashed_password})
        save_users(users)
        flash("Registration successful! Please login.")
        return redirect(url_for("user_login"))

    return render_template("register.html")

@app.route("/user-logout")
def user_logout():
    session.pop("user", None)
    return redirect(url_for("index"))

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        admins = load_admins()

        for admin in admins:
            if admin["username"] == username and check_password_hash(admin["password"], password):
                session["admin"] = username
                session["admin_user"] = {
                    "username": username,
                    "business": admin.get("business", ""),
                    "category": admin.get("category", ""),
                    "logo": admin.get("logo", "")
                }
                return redirect(url_for("admin_panel"))

        error = "Invalid credentials"
    return render_template("admin_login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    session.pop("admin_user", None)
    return redirect(url_for("index"))

@app.route("/admin")
def admin_panel():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    query = request.args.get("search", "").lower().strip()
    menu = load_json(MENU_FILE)
    orders = load_json(ORDERS_FILE)

    current_admin_username = session["admin"]

    # Filter this admin's menu items
    admin_items = [item for item in menu if item.get("admin") == current_admin_username]

    # Filter orders that include this admin's items
    admin_order_count = 0
    admin_total_revenue = 0

    for order in orders:
        admin_order_total = 0
        matched = False
        for item in order["items"]:
            # match by admin username (added when item is saved to menu)
            matching_menu_item = next((m for m in admin_items if m["name"] == item["name"]), None)
            if matching_menu_item:
                matched = True
                admin_order_total += item["price"] * item["quantity"]
        if matched:
            admin_order_count += 1
            admin_total_revenue += admin_order_total

    if query:
        admin_items = [
            item for item in admin_items
            if query in item.get("name", "").lower()
            or query in item.get("category", "").lower()
        ]

    return render_template(
        "admin_panel.html",
        menu=admin_items,
        total_orders=admin_order_count,
        total_revenue=admin_total_revenue,
        search_query=query
    )



@app.route("/admin/add-item", methods=["POST"])
def add_item():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    name = request.form["name"]
    price = float(request.form["price"])
    category = request.form["category"]
    image_file = request.files["image_file"]

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if image_file.filename == "":
        flash("No file selected.")
        return redirect(url_for("admin_panel"))

    filename = secure_filename(image_file.filename)
    image_file.save(os.path.join(UPLOAD_FOLDER, filename))
    # Save only 'filename' in item['image']
    menu = load_json(MENU_FILE)
    menu.append({
        "id": str(uuid.uuid4()),
        "name": name,
        "price": price,
        "image": filename,
        "category": category,
        "restaurant_name": session.get("admin_user", {}).get("business", ""),
        "admin": session["admin"]
    })
    save_json(MENU_FILE, menu)
    flash("Item added successfully!")
    return redirect(url_for("admin_panel"))

@app.route("/admin/delete-item/<item_id>")
def delete_item(item_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    menu = load_json(MENU_FILE)
    item_to_delete = next((i for i in menu if i["id"] == item_id and i.get("admin") == session["admin"]), None)
    if item_to_delete:
        image_path = os.path.join(UPLOAD_FOLDER, item_to_delete["image"])
        if os.path.exists(image_path):
            os.remove(image_path)
        menu = [i for i in menu if i["id"] != item_id]
        save_json(MENU_FILE, menu)

    return redirect(url_for("admin_panel"))

@app.route("/edit/<item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    menu = load_json(MENU_FILE)
    item = next((i for i in menu if i.get("id") == item_id and i.get("admin") == session["admin"]), None)

    if not item:
        return "Item not found", 404

    if request.method == "POST":
        item["name"] = request.form["name"]
        item["price"] = float(request.form["price"])
        item["category"] = request.form["category"]

        image_file = request.files.get("image_file")
        if image_file and image_file.filename:
            ext = os.path.splitext(image_file.filename)[1]
            new_filename = f"{uuid.uuid4().hex}{ext}"
            new_image_path = os.path.join(UPLOAD_FOLDER, new_filename)
            image_file.save(new_image_path)

            old_image_path = os.path.join(UPLOAD_FOLDER, item["image"])
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

            item["image"] = new_filename

        save_json(MENU_FILE, menu)
        flash("Item updated successfully!")
        return redirect(url_for("admin_panel"))

    return render_template("edit_item.html", item=item)

@app.route("/admin_register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        business = request.form["business"]
        category = request.form["category"]

        admins = load_admins()
        if any(a["username"] == username for a in admins):
            flash("Username already exists.", "danger")
            return render_template("admin_register.html")

        # Generate logo for the admin
        logo_filename = f"{uuid.uuid4().hex}.png"
        generate_admin_logo(business, logo_filename)

        new_admin = {
            "username": username,
            "password": generate_password_hash(password),
            "business": business,
            "category": category,
            "logo": logo_filename
        }
        admins.append(new_admin)
        save_admins(admins)
        flash("Admin registered successfully!", "success")
        return redirect(url_for("index"))

    return render_template("admin_register.html")

# Helpers
def load_json(file):
    if not os.path.exists(file): return []
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_logo(business_name):
    img = Image.new("RGB", (400, 100), color=(255, 165, 0))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    d.text((10, 25), business_name, fill=(255, 255, 255), font=font)
    logo_name = f"{uuid.uuid4().hex}.png"
    logo_path = os.path.join(LOGO_FOLDER, logo_name)
    img.save(logo_path)
    return logo_name

def generate_admin_logo(business_name, filename):
    width, height = 400, 120
    background_color = (255, 255, 255)
    text_color = (255, 87, 34)  # QuickBite orange
    font_size = 40

    img = Image.new("RGB", (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    try:
        font_path = "arial.ttf"
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # Use textbbox for accurate text size (Pillow >=8.0)
    bbox = draw.textbbox((0, 0), business_name, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    draw.text((x, y), business_name, fill=text_color, font=font)

    os.makedirs(LOGO_FOLDER, exist_ok=True)
    image_path = os.path.join(LOGO_FOLDER, filename)
    img.save(image_path)

# Super Admin Login
@app.route("/superadmin-login", methods=["GET", "POST"])
def superadmin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "superadmin" and password == "superadmin123":
            session["superadmin"] = True
            return redirect(url_for("superadmin_dashboard"))
        flash("Invalid credentials")
    return render_template("superadmin/superadmin_login.html")

@app.route("/superadmin-logout")
def superadmin_logout():
    session.pop("superadmin", None)
    return redirect(url_for("superadmin_login"))

@app.route("/superadmin")
def superadmin_dashboard():
    if not session.get("superadmin"):
        return redirect(url_for("superadmin_login"))

    admins = load_json(ADMIN_FILE)
    users = load_json(USERS_FILE)
    menu = load_json(MENU_FILE)
    orders = load_json(ORDERS_FILE)

    # 📊 Build a summary of orders and revenue per business
    revenue_map = {}  # {restaurant_name: {orders: X, revenue: Y}}

    for order in orders:
        for item in order.get("items", []):
            restaurant = item.get("restaurant_name")
            if restaurant:
                if restaurant not in revenue_map:
                    revenue_map[restaurant] = {"orders": 0, "revenue": 0}
                revenue_map[restaurant]["orders"] += 1
                revenue_map[restaurant]["revenue"] += item["price"] * item["quantity"]

    # 📎 Attach revenue info to each admin
    for admin in admins:
        business = admin.get("business")
        summary = revenue_map.get(business, {"orders": 0, "revenue": 0})
        admin["total_orders"] = summary["orders"]
        admin["total_revenue"] = summary["revenue"]

    return render_template(
        "superadmin/superadmin_dashboard.html",
        admins=admins,
        users=users,
        menu=menu,
        orders=orders
    )


@app.route("/superadmin/delete-admin/<username>")
def delete_admin(username):
    if not session.get("superadmin"):
        return redirect(url_for("superadmin_login"))
    admins = load_json(ADMIN_FILE)
    admins = [a for a in admins if a["username"] != username]
    save_json(ADMIN_FILE, admins)
    return redirect(url_for("superadmin_dashboard"))

@app.route("/superadmin/delete-user/<username>")
def delete_user(username):
    if not session.get("superadmin"):
        return redirect(url_for("superadmin_login"))
    users = load_json(USERS_FILE)
    users = [u for u in users if u["username"] != username]
    save_json(USERS_FILE, users)
    return redirect(url_for("superadmin_dashboard"))

@app.route("/superadmin/delete-menu/<item_id>")
def superadmin_delete_menu(item_id):
    if not session.get("superadmin"):
        return redirect(url_for("superadmin_login"))

    menu = load_json(MENU_FILE)

    # Safely filter without crashing if "id" is missing
    menu = [item for item in menu if item.get("id") != item_id]

    save_json(MENU_FILE, menu)
    flash("Menu item deleted successfully!")
    return redirect(url_for("superadmin_dashboard"))


@app.route("/superadmin/add-admin", methods=["GET", "POST"])
def add_admin():
    if not session.get("superadmin"):
        return redirect(url_for("superadmin_login"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        business = request.form["business"]
        category = request.form["category"]

        admins = load_json(ADMIN_FILE)
        if any(a["username"] == username for a in admins):
            flash("Admin already exists.")
            return redirect(url_for("add_admin"))

        logo_filename = f"{uuid.uuid4().hex}.png"
        generate_admin_logo(business, logo_filename)

        admins.append({
            "username": username,
            "password": generate_password_hash(password),
            "business": business,
            "category": category,
            "logo": logo_filename
        })
        save_json(ADMIN_FILE, admins)
        flash("Admin added successfully.")
        return redirect(url_for("superadmin_dashboard"))

    return render_template("superadmin/add_admin.html")

if __name__ == "__main__":
    app.run(debug=True)



