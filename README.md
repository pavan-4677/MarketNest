# MarketNest - Online Community Marketplace

> **"Buy Local. Sell Smart."**

MarketNest is a full-featured, production-style community marketplace web application built with **Python**, **Django**, and **Bootstrap 5**. It enables neighbors and local communities to buy, sell, and discover pre-loved products safely and sustainably without middlemen or commission fees.

---

## 🌟 Key Features

### 👤 User Authentication & Profile Management
- **Registration & Login**: Secure Django authentication with password hashing, email validation, and confirm-password verification.
- **User Dashboard**: Metrics dashboard tracking **My Listings**, **Active Listings**, **Total Views**, and **Saved Favorites**, plus recent inquiries and quick-action shortcuts.
- **Custom Profile**: User bio, phone/WhatsApp number, neighborhood location, and profile avatar upload with UI-Avatar fallbacks.
- **Public Seller Profile**: Dedicated public profile page (`/seller/<username>/`) displaying seller bio, verified member badge, join date, and active listings.

### 📦 Dynamic Marketplace & Listing Management (CRUD)
- **Create Listing**: Easy form to post products with title, category, condition (*New, Like New, Good, Fair, Used*), price, neighborhood location, description, primary photo, and optional additional gallery images.
- **Ownership Authorization**: Strict permission checks ensuring users can only edit or delete their own listings.
- **Direct Mobile & WhatsApp Contact**: Sellers can provide their mobile number; buyers can click to call directly or initiate a WhatsApp chat with prefilled listing details.
- **Mark as Sold**: Toggle listing status between *Active* and *Sold/Inactive* with a single click.
- **Delete Confirmation Modal**: Confirmation dialogs preventing accidental deletions.
- **Image Security & Validation**: Strict validation for file extensions (`.jpg`, `.jpeg`, `.png`, `.webp`) and maximum file size (5MB).

### 🔍 Advanced Real Database Search & Filtering
- **Keyword Search**: Real-time database queries matching product title, description, category, and location.
- **Category Filter**: Filter listings dynamically across 9 marketplace categories.
- **Price Range Filter**: Minimum and maximum price filtering with database query constraints.
- **Condition Filter**: Filter by product wear (*Brand New*, *Like New*, *Good*, etc.).
- **City / Neighborhood Filter**: Local community filtering.
- **Sorting Options**: Sort by *Newest First*, *Price: Low to High*, *Price: High to Low*, and *Most Popular (Views)*.
- **Pagination**: 12 listings per page with query-parameter preservation across pagination links.

### ❤️ Interactive Favorites & Buyer-Seller Communication
- **AJAX Heart Toggle**: Save or remove items from favorites instantly without page reload; dynamic navbar counter update.
- **Favorites Page**: Dedicated page displaying all bookmarked listings.
- **Product Inquiries**: Direct in-app messaging between buyers and sellers on the product detail page, storing inquiries in the database and notifying the seller on their dashboard.

### 🛡️ Administrative Control & Data Integrity
- **Django Admin Portal**: Full-featured admin customization with list filters, searchable fields, inline gallery management, and batch actions to activate/deactivate listings.
- **Zero Static Cards**: 100% of products, categories, users, views, and favorites are driven by Django ORM queries.
- **No Broken Media**: Automated seed command generates authentic, high-quality images directly into `MEDIA_ROOT`.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.10+, Django 5.x / 6.x, Django ORM, Django Auth, Django Messages |
| **Database** | SQLite (default for development), structured for seamless MySQL switch |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla ES6), Bootstrap 5.3, Bootstrap Icons |
| **Typography** | Google Fonts (*Plus Jakarta Sans*) |
| **Image Processing** | Pillow (PIL) |

---

## 📁 Project Structure

```
marketnest/
│
├── manage.py                       # Django CLI utility
├── requirements.txt                # Project dependencies
├── test_system.py                  # Automated 10-point test suite
├── db.sqlite3                      # SQLite database file
│
├── marketnest/                     # Project configuration
│   ├── __init__.py
│   ├── settings.py                 # Core settings (Database, Static, Media, Auth)
│   ├── urls.py                     # Root routing & custom 404/500 handlers
│   ├── wsgi.py
│   └── asgi.py
│
├── marketplace/                    # Main Marketplace Application
│   ├── __init__.py
│   ├── admin.py                    # Django Admin configuration & batch actions
│   ├── apps.py                     # App configuration & signal registration
│   ├── context_processors.py       # Global categories, unread count & user favorites
│   ├── forms.py                    # Registration, Login, Product, Profile, Inquiries
│   ├── models.py                   # Category, Profile, Product, ProductImage, Favorite, ContactMessage
│   ├── signals.py                  # Auto-create user Profile signal
│   ├── urls.py                     # Marketplace endpoints
│   ├── views.py                    # Complete view logic (CRUD, Search, Dashboard)
│   └── management/
│       └── commands/
│           ├── __init__.py
│           └── seed_data.py        # Database seeder with realistic data & images
│
├── templates/                      # Modular HTML Templates
│   ├── base.html                   # Master layout (Sticky navbar, toasts, footer)
│   ├── 404.html                    # Custom 404 error page
│   ├── 500.html                    # Custom 500 error page
│   └── marketplace/
│       ├── home.html               # Hero, category shortcuts, featured ads, features
│       ├── products.html           # Browse, multi-filter sidebar, search, sorting
│       ├── product_detail.html     # Image gallery, seller card, contact modal, similar ads
│       ├── login.html              # Custom authentication page
│       ├── register.html           # Registration with validation
│       ├── dashboard.html          # Stats cards, recent listings, recent inquiries
│       ├── create_listing.html     # Add product listing form with live image preview
│       ├── edit_listing.html       # Edit ad form & status toggle
│       ├── my_listings.html        # Filter tabs (All/Active/Sold) & delete modal
│       ├── favorites.html          # Saved items grid
│       ├── profile.html            # Profile info & avatar upload
│       ├── seller_profile.html     # Public seller page with active items
│       ├── about.html              # Brand story & values
│       └── contact.html            # Support contact form & FAQs
│
├── static/
│   ├── css/
│   │   └── style.css               # Design system tokens, micro-animations, card hover
│   └── js/
│       └── main.js                 # AJAX favorites, gallery thumbnail switcher, image previews
│
└── media/                          # Uploaded and seeded media files
    └── products/                   # Product banner photos
```

---

## 🚀 Quick Setup & Installation

### Step 1: Clone or Navigate to the Project
```bash
cd Project
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Seed Demo Database (Idempotent)
Run the custom seed command to automatically create demo users, categories, 16 realistic listings with local images, favorites, and inquiries:
```bash
python manage.py seed_data
```

### Step 6: Start the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to: **`http://127.0.0.1:8000/`**

---

## 🔑 Demo Accounts & Credentials

| Role | Username | Password | Email | Notes |
|---|---|---|---|---|
| **Super Admin** | `admin` | `admin123` | `admin@marketnest.com` | Access Django Admin at `/admin/` |
| **Demo Seller 1** | `rahul` | `demo12345` | `rahul@example.com` | Bengaluru (Tech & Electronics) |
| **Demo Seller 2** | `priya` | `demo12345` | `priya@example.com` | Mumbai (Furniture & Decor) |
| **Demo Seller 3** | `arjun` | `demo12345` | `arjun@example.com` | Delhi (Sports & Fitness) |
| **Demo Seller 4** | `sneha` | `demo12345` | `sneha@example.com` | Hyderabad (Fashion & Gear) |

---

## 🗄️ Switching to MySQL Database (Production Ready)

To switch from SQLite to MySQL:

1. Install MySQL driver:
   ```bash
   pip install mysqlclient
   ```
2. In `marketnest/settings.py`, replace the `DATABASES` dictionary with:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'marketnest_db',
           'USER': 'marketnest_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '3306',
           'OPTIONS': {
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
               'charset': 'utf8mb4',
           }
       }
   }
   ```
3. Run migrations and seed data:
   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```

---

## 🧪 Automated Testing

A comprehensive verification test suite is included in `test_system.py`. Run it at any time to verify authentication, CRUD operations, permissions, favorites, and inquiries:

```bash
python test_system.py
```

Expected output:
```
[OK] rahul login successful
[OK] Dashboard loaded for authenticated user
[OK] Create listing successful!
[OK] Edit listing successful!
[OK] Toggle listing status (Mark as sold) successful!
[OK] Delete listing successful!
[OK] Favorite toggle AJAX successful!
[OK] Contact seller inquiry message successfully saved in DB!
[OK] User registration and auto-login successful!
[OK] Search and Category filter query successful!

========================================================
ALL 10 VERIFICATION TESTS PASSED PERFECTLY!
========================================================
```

---

## 💼 Resume-Ready Project Description

> **MarketNest – Online Community Marketplace Web Application (Django, Python, Bootstrap 5)**
> - Engineered a full-stack peer-to-peer community marketplace facilitating neighborhood commerce across 9 product categories.
> - Implemented secure Django authentication, user profiles, dashboard metrics, and ownership-protected CRUD operations for product listings.
> - Developed real-time database search and multi-faceted filtering (category, price range, condition, location) with dynamic query preservation and pagination.
> - Built interactive features including AJAX-driven listing bookmarking (favorites), buyer-seller product inquiry messaging, and a multi-image gallery switcher.
> - Architected a mobile-responsive UI with custom CSS design tokens, Bootstrap 5, micro-interactions, and Django Admin management with batch actions.

---

## 📄 License
This project is open-source and built for educational and portfolio demonstration purposes. All rights reserved &copy; 2026 **MarketNest**.
