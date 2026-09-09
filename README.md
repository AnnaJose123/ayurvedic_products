# Ayurvedic Products Website - HerbaCare

[![Django Version](https://img.shields.io/badge/Django-6.1-2E5A27?logo=django)](https://www.djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.14-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A complete, responsive, and professional full-stack **Ayurvedic Products Web Application** developed using **Python, Django, Django ORM, HTML5, CSS3, JavaScript, and SQLite**. Designed specifically for showcasing and enquiring about authentic herbal personal-care products such as Herbal Hair Oil, Ayurvedic Face Pack, Herbal Shampoo, and Ayurvedic Body Oil.

Developed by GitHub user: **[AnnaJose123](https://github.com/AnnaJose123)**.

---

## 🌿 Key Features & Architectural Highlights

- **Dynamic Django ORM Data Flow**: Product catalog and customer enquiries are managed dynamically through Django ORM and SQLite. No product details are hard-coded in HTML templates.
- **WhatsApp Click-to-Chat Integration**: Built-in dynamic WhatsApp URL generator (`https://wa.me/<NUMBER>?text=<ENCODED_MESSAGE>`).
  - Pre-filled message with product name & price on product cards and detail pages.
  - Pre-filled message with customer name, phone, product, and message upon form submission.
  - Business WhatsApp number configurable in `settings.py` (`WHATSAPP_NUMBER = "919876543210"`).
- **Responsive Ayurvedic Visual Aesthetic**:
  - Earthy, natural visual design palette (Forest Green `#2E5A27`, Sage, Sand Cream, Warm Gold).
  - Modern typography powered by Google Fonts (*Playfair Display* & *Plus Jakarta Sans*).
  - Card elevation, hover zoom effects, and sticky header with mobile drawer hamburger menu.
  - Optimized for Desktop, Laptop, Tablet, and Mobile viewport widths.
- **Dedicated Product Detail Pages**: Accessible via clean SEO-friendly URLs (`/products/<slug>/`).
- **Customer Enquiry Management**: Custom `EnquiryForm` subclassing `forms.ModelForm` with validation:
  - **Name**: Required, minimum length, non-numeric validation.
  - **Phone**: Validates 10-digit Indian phone numbers (e.g. `9876543210` or `+919876543210`).
  - **Message**: Required non-empty message with length bounds.
  - **Database Storage**: Submitted enquiries are saved directly to SQLite and accessible in Django Admin.
- **Comprehensive Django Admin Dashboard**:
  - Manage products (Add, edit, delete, set availability, upload images, update prices).
  - View customer enquiries with date filter and search.
- **Complete Test Coverage**: Includes 11 automated unit tests covering models, forms, views, and WhatsApp URL generation (`python manage.py test`).

---

## 📁 Project Structure

```text
ayurvedic_products/
│
├── manage.py
├── seed_data.py
├── create_admin.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── ayurvedic_products/
│   ├── __init__.py
│   ├── settings.py          # App configs, static/media paths, WHATSAPP_NUMBER
│   ├── urls.py              # Root routing & static media server
│   ├── asgi.py
│   └── wsgi.py
│
├── products/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── templates/
│   │   └── products/
│   │       ├── base.html             # Base layout, sticky header & footer
│   │       ├── home.html             # Hero, About, Products grid, Enquiry form, Contact
│   │       ├── product_detail.html   # Single product detailed showcase page
│   │       └── enquiry_success.html  # Enquiry confirmation card + WhatsApp action
│   │
│   ├── static/
│   │   └── products/
│   │       ├── css/
│   │       │   └── style.css         # Natural green Ayurvedic design system
│   │       ├── js/
│   │       │   └── script.js         # Mobile drawer toggle & smooth scrolling
│   │       └── images/
│   │
│   ├── admin.py             # ProductAdmin & EnquiryAdmin configurations
│   ├── apps.py
│   ├── forms.py             # EnquiryForm with custom validation logic
│   ├── models.py            # Product & Enquiry Django models
│   ├── utils.py             # WhatsApp URL generator helpers
│   ├── urls.py              # App URL patterns (/products/<slug>/, /enquiry/, etc.)
│   ├── views.py             # Home, Detail, Enquiry & Success view handlers
│   └── tests.py             # Automated unit test suite
│
├── media/
│   └── products/            # Uploaded and seeded product image files
│
└── static/                  # Root static assets directory
```

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14+, Django 6.1
- **ORM & Database**: Django ORM, SQLite
- **Frontend**: HTML5, Vanilla CSS3 (Custom CSS Variables & Flex/Grid), JavaScript (ES6)
- **Image Handling**: Pillow
- **Version Control**: Git & GitHub (`AnnaJose123`)

---

## 🚀 Quick Start & Installation Guide

Follow these steps to run the project locally on Windows, macOS, or Linux:

### 1. Clone the Repository
```bash
git clone https://github.com/AnnaJose123/ayurvedic_products.git
cd ayurvedic_products
```

### 2. Create and Activate a Virtual Environment
**On Windows (PowerShell / Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Sample Products & Media Images
Run the included seed script to generate sample product images and populate SQLite with 4 initial Ayurvedic products (Herbal Hair Oil, Ayurvedic Face Pack, Herbal Shampoo, Ayurvedic Body Oil):
```bash
python seed_data.py
```

### 6. Create Default Admin Superuser
Run the administrative user generator:
```bash
python create_admin.py
```
> **Default Admin Credentials:**
> - **Username**: `admin`
> - **Password**: `adminpassword123`
> - **Email**: `admin@herbacare.com`

### 7. Run the Development Server
```bash
python manage.py runserver
```

Open your browser and visit:
- **Website Home**: [http://127.0.0.1:8000/](http://127.0.0.1:8001/)
- **Django Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Running Automated Unit Tests

To run the automated test suite and check model, view, form, and WhatsApp logic:
```bash
python manage.py test
```

Expected output:
```text
Ran 11 tests in 0.050s
OK
```

---

## 📱 WhatsApp Integration Setup

The business WhatsApp phone number is configured globally in `ayurvedic_products/settings.py`:

```python
# WhatsApp Business Integration Number (International Format, no +, spaces, or hyphens)
WHATSAPP_NUMBER = "919876543210"
```

To update the business number for live operations, simply change this setting to your international phone number (e.g. `919876543210` for India).

---

## ⚙️ Django Admin Usage Guide

1. Log in to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).
2. Under **Products**:
   - Click **Add Product** to create new items.
   - Edit prices, descriptions, categories, availability status, or upload custom images.
   - Slugs are automatically generated from product names.
3. Under **Customer Enquiries**:
   - Inspect all user form submissions with customer names, phone numbers, selected products, and timestamps.

---

## 📄 License & Attribution

Developed for HerbaCare Ayurvedic Products.  
Author: [AnnaJose123](https://github.com/AnnaJose123)
