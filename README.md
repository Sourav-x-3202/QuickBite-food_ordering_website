# 🍔 QuickBite

**QuickBite** is a full-stack, multi-role food ordering web application designed for restaurants, food vendors, and digital ordering services. Built with Python's **Flask framework**, it features a **modular architecture**, **local file storage**, and **role-based access** for **Customers**, **Restaurant Admins**, and a **Super Admin**. QuickBite is fully self-contained and works offline, making it suitable for lightweight POS systems and standalone deployments.

---

## 📌 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture-overview)
- [Technology Stack](#-technology-stack)
- [Roles & Responsibilities](#-roles--responsibilities)
- [Folder Structure](#-folder-structure)
- [Setup Instructions](#-setup-instructions)
- [Usage Workflow](#-usage-workflow)
- [Screenshots](#-screenshots)
- [To-Do / Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## ✨ Features

### 🔒 Authentication & Role Management
- Separate login and registration for **Users**, **Admins**, and **Super Admin**
- Secure session management with automatic role segregation
- Password masking and validation

### 🍽️ Menu Management
- Admins can **create**, **edit**, and **delete** menu items
- Upload and display **food item images**
- Auto-generated restaurant **logo creation** for brand identity

### 🛒 Customer Ordering
- Real-time cart functionality with live item count
- "Add to Cart" and "Order Now" workflows
- Menu filtering and responsive layout for all devices

### 📦 Order Management
- Orders are stored per-user and per-admin
- Admins can view and track orders placed through their restaurant
- Orders stored locally as JSON for persistence and analysis

### 🧑‍✈️ Super Admin Privileges
- Global access to **all admin data**, **menu items**, and **user orders**
- Control panel for monitoring platform activity
- Admin onboarding and deletion

---

## 🧠 Architecture Overview

QuickBite is structured into **three isolated logical layers**, with **clean routing** and **template inheritance**:

```
Users ↔ Flask Routes ↔ Templates (Jinja2)
     ↕               ↕
Local JSON Files  ⟷ Static Uploads
```

- No cloud database used — all user data, menu items, and orders are stored locally in JSON format.
- Images are stored in local folders (`/static/uploads` and `/static/logos`).
- Flask `session` handles secure authentication and role tracking.
- Code is modular and split by role: `user`, `admin`, and `superadmin`.

---

## 🧰 Technology Stack

| Component     | Tech/Tool        |
|---------------|------------------|
| Framework     | Flask (Python)   |
| Frontend      | HTML, CSS, JS    |
| Template Engine | Jinja2         |
| Data Storage  | JSON (local)     |
| Image Handling| Pillow (PIL)     |
| File Uploads  | Flask `request.files` |
| Styling       | Custom CSS per role |
| Sessions      | Flask `session` module |

---

## 🔐 Roles & Responsibilities

### 👤 Customer
- Register / Login
- Browse menu items by category
- Add to cart, place orders
- View live cart count and feedback

### 🧑‍🍳 Restaurant Admin
- Register their restaurant (with auto logo creation)
- Login → Manage Menu → View Orders

### 👑 Super Admin
- Login → View all admins, menus, and orders → Full control access

---

## 📁 Folder Structure

```
quickbite/
│
├── app.py                         # Main Flask app (all routes unified)
├── data/                          # Local persistent storage
│   ├── users.json
│   ├── admins.json
│   ├── superadmins.json
│   ├── menu_admin.json
│   └── orders_user.json
├── static/
│   ├── css/
│   │   ├── user.css
│   │   ├── admin.css
│   │   └── superadmin.css
│   ├── uploads/
│   └── logos/
├── templates/
│   ├── user/
│   ├── admin/
│   └── superadmin/
├── screenshots/
└── README.md
```

---

## ⚙️ Setup Instructions

### ✅ Prerequisites
- Python 3.8 or above
- `pip` package manager
- Git

### 🔧 Installation Steps

```bash
# Clone the repository
git clone https://github.com/your-username/quickbite.git
cd quickbite

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install Flask Pillow
```

### ▶️ Run the Application

```bash
python app.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) to begin.

---

## 🔄 Usage Workflow

1. **User Flow**: Register → Login → Browse Menu → Add to Cart → Place Order
2. **Admin Flow**: Register (auto logo created) → Login → Manage Menu → View Orders
3. **Super Admin Flow**: Login → View all admins, menus, and orders → Full control

---

## 🖼️ Screenshots

| Customer Menu | Admin Dashboard | Super Admin Panel |
|---------------|------------------|--------------------|
| ![](screenshots/user_menu.png) | ![](screenshots/admin_dash.png) | ![](screenshots/superadmin.png) |

---

## 📈 Roadmap

- [ ] Add order history & tracking for users
- [ ] Search, filter, and sort menus and orders
- [ ] Responsive pagination for large data sets
- [ ] QR-based table ordering (optional)
- [ ] SQLite or PostgreSQL backend integration
- [ ] Deployable version with Docker / Railway

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make changes and commit
4. Push and open a Pull Request

---

## ⚖️ License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Mannu**  
Developer & Maintainer  
📧 your.email@example.com  
🌐 [GitHub Profile](https://github.com/your-username)