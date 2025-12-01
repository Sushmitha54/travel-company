# 🚗 Travel Company Ride-Share Website

A Flask-based platform that connects travelers at stations (railway, bus stop, metro, etc.) going to the same destination so they can share rides and reduce travel costs.

---

## 🌟 Features

* 🔍 **Find Rides** — View available rides based on location and destination.
* 👥 **Join a Ride Group** — Connect with travelers going to the same place.
* 📝 **User Registration & Login** — Secure authentication system.
* 🎨 **Beautiful, colorful UI** — Clean, responsive interface.
* 🗄 **SQLite/PostgreSQL Database Support** — Flexible storage.
* 🌐 **Deployable on Render / Railway / GitHub** — Easy cloud hosting.

---

## 🏠 Pages Included

* **Home Page** — Overview and navigation
* **Register Page** — Create a new account
* **Login Page** — Login securely
* **Find Rides Page** — Search and join rides

All pages are styled for a modern, vibrant look.

---

## 🗄 Database Setup

### SQLite (Local Development)

* Database file located inside `instance/app.db`
* Auto-created when you run the Flask app

### PostgreSQL (Production on Render)

Set the following environment variable:

```
DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>
```

The app automatically connects when deployed.

---

## � Deployment (Render)

1. Push code to GitHub
2. Visit [https://render.com](https://render.com)
3. Create a **New Web Service**
4. Con
