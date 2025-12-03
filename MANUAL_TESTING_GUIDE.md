# Manual Testing Guide - Travel Company Ride-Share System

## 📋 Overview
This guide provides step-by-step manual testing procedures for the Travel Company booking system. All tests should be performed on a local development environment.

## 🛠️ Setup Instructions

### 1. Environment Setup
```bash
cd travel-company
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 2. Access URLs
- **Main Application**: http://127.0.0.1:5000
- **Admin Panel**: http://127.0.0.1:5000/admin (after setup)

## 🧪 Test Cases

### **TC-001: User Registration**
**Priority:** High
**Preconditions:** None
**Test Steps:**
1. Navigate to http://127.0.0.1:5000
2. Click "Register" link
3. Fill registration form:
   - Name: "Test User"
   - Email: "testuser@example.com"
   - Contact: "9876543210"
   - Password: "password123"
   - Confirm Password: "password123"
4. Click "Register"

**Expected Results:**
- ✅ Redirect to login page
- ✅ Success message: "Account created. Please log in."
- ✅ Email confirmation sent (if email configured)

**Pass/Fail Criteria:**
- [ ] Registration successful
- [ ] No validation errors
- [ ] Database entry created

---

### **TC-002: User Login**
**Priority:** High
**Preconditions:** User registered (TC-001)
**Test Steps:**
1. Navigate to login page
2. Enter credentials:
   - Email: "testuser@example.com"
   - Password: "password123"
3. Click "Login"

**Expected Results:**
- ✅ Redirect to dashboard
- ✅ Welcome message displayed
- ✅ Session maintained

---

### **TC-003: Successful Ride Booking**
**Priority:** Critical
**Preconditions:** User logged in
**Test Steps:**
1. Click "Book Ride" from navigation
2. Fill booking form:
   - Name: "John Doe"
   - Location: Select "Central Station"
   - Destination: "Airport Terminal"
   - Date: Select future date (7 days ahead)
   - Time: "14:30"
   - Passengers: "2"
   - Contact: "9876543210"
3. Click "Book Ride"

**Expected Results:**
- ✅ Booking confirmation page displayed
- ✅ Booking ID generated
- ✅ Email notification sent
- ✅ Database entry created with status "pending"

---

### **TC-004: Booking Validation Errors**
**Priority:** High
**Preconditions:** User logged in
**Test Steps:**
1. Navigate to Book Ride page
2. Submit form with invalid data:
   - Name: (leave empty)
   - Location: (leave empty)
   - Date: Past date
   - Passengers: "10" (exceeds limit)
   - Contact: "123" (too short)

**Expected Results:**
- ✅ Form validation errors displayed
- ✅ No booking created
- ✅ User-friendly error messages

---

### **TC-005: View My Bookings**
**Priority:** High
**Preconditions:** User has bookings (TC-003)
**Test Steps:**
1. Click "My Bookings" from navigation
2. Verify booking details displayed
3. Check booking status and information

**Expected Results:**
- ✅ All user bookings listed
- ✅ Correct booking details shown
- ✅ Status badges displayed
- ✅ Action buttons available

---

### **TC-006: Cancel Booking (Valid)**
**Priority:** High
**Preconditions:** User has future booking >2 hours away
**Test Steps:**
1. Go to My Bookings page
2. Click "Cancel" on a valid booking
3. Confirm cancellation in modal

**Expected Results:**
- ✅ Booking status changes to "cancelled"
- ✅ Cancellation email sent
- ✅ Success message displayed
- ✅ Booking removed from active list

---

### **TC-007: Cancel Booking (Too Late)**
**Priority:** Medium
**Preconditions:** User has booking <2 hours away
**Test Steps:**
1. Attempt to cancel booking close to travel time
2. Confirm cancellation

**Expected Results:**
- ✅ Cancellation blocked
- ✅ Error message: "Cannot cancel booking less than 2 hours before travel"
- ✅ Booking status unchanged

---

### **TC-008: Ride Posting and Joining**
**Priority:** Medium
**Preconditions:** User logged in
**Test Steps:**
1. Click "Find Rides" from navigation
2. Fill ride form:
   - Name: "Ride to Airport"
   - Location: "Central Station"
   - Destination: "Airport Terminal"
   - Contact: "9876543210"
3. Click "Create Ride"
4. Login as different user
5. Go to Book Ride page
6. Click "Join Ride" on the posted ride

**Expected Results:**
- ✅ Ride appears in available groups
- ✅ Join successful
- ✅ User added to ride passengers
- ✅ Confirmation message displayed

---

### **TC-009: Anonymous Booking**
**Priority:** Medium
**Preconditions:** None (user not logged in)
**Test Steps:**
1. Navigate to Book Ride page (without logging in)
2. Fill booking form with valid data
3. Submit booking

**Expected Results:**
- ✅ Booking created successfully
- ✅ Booking ID generated
- ✅ Access to confirmation page allowed

---

### **TC-010: Unauthorized Access Prevention**
**Priority:** High
**Preconditions:** None
**Test Steps:**
1. Without logging in, try to access:
   - /my_bookings
   - /dashboard
   - /admin (if exists)
2. Try to cancel another user's booking
3. Try to view another user's booking confirmation

**Expected Results:**
- ✅ Redirect to login page
- ✅ Error messages for unauthorized actions
- ✅ No data leakage

---

### **TC-011: Email Notifications**
**Priority:** Medium
**Preconditions:** Email configured, booking created
**Test Steps:**
1. Create a booking
2. Check email inbox for:
   - Booking confirmation email
   - Admin notification email
3. Cancel a booking
4. Check for cancellation email

**Expected Results:**
- ✅ HTML emails received
- ✅ Correct booking details in email
- ✅ Professional email formatting
- ✅ No email errors in logs

---

### **TC-012: Admin Dashboard Access**
**Priority:** High
**Preconditions:** Admin user exists
**Test Steps:**
1. Login as admin user
2. Navigate to /admin
3. View users, bookings, analytics

**Expected Results:**
- ✅ Admin panel accessible
- ✅ All data displayed correctly
- ✅ Analytics charts rendered
- ✅ CRUD operations work

---

### **TC-013: Payment Integration (if implemented)**
**Priority:** High
**Preconditions:** Payment gateway configured
**Test Steps:**
1. Create booking
2. Proceed to payment
3. Complete payment flow
4. Verify payment status

**Expected Results:**
- ✅ Payment gateway loads
- ✅ Transaction successful
- ✅ Payment status updated
- ✅ Transaction ID stored

---

### **TC-014: Real-time Features (if implemented)**
**Priority:** Medium
**Preconditions:** WebSocket enabled
**Test Steps:**
1. Open two browser windows
2. Login as different users
3. Post/join rides
4. Verify real-time updates

**Expected Results:**
- ✅ Live notifications appear
- ✅ Chat messages update instantly
- ✅ No page refresh needed

---

### **TC-015: Mobile Responsiveness**
**Priority:** Medium
**Preconditions:** None
**Test Steps:**
1. Open application on mobile device/browser
2. Test all forms and navigation
3. Verify layout adapts to small screens

**Expected Results:**
- ✅ All pages mobile-friendly
- ✅ Forms usable on mobile
- ✅ No horizontal scrolling

---

### **TC-016: Error Recovery**
**Priority:** Medium
**Preconditions:** None
**Test Steps:**
1. Submit forms with network disconnected
2. Try invalid URLs
3. Test server restart scenarios
4. Verify error pages display correctly

**Expected Results:**
- ✅ Graceful error handling
- ✅ User-friendly error messages
- ✅ No application crashes

## 🧪 Automated Testing

### Running Unit Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_booking.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run integration tests only
pytest -m integration
```

### Test Coverage Requirements
- **Models**: 90%+ coverage
- **Routes**: 85%+ coverage
- **Forms**: 95%+ coverage
- **Overall**: 80%+ coverage

## 🐛 Bug Reporting

When reporting bugs, include:
- Test case ID
- Steps to reproduce
- Expected vs actual results
- Browser/console errors
- Screenshots if applicable
- Environment details

## ✅ Test Completion Checklist

- [ ] All high-priority tests passed
- [ ] No critical bugs found
- [ ] Email notifications working
- [ ] Admin panel functional
- [ ] Payment integration tested
- [ ] Mobile responsiveness verified
- [ ] Performance acceptable
- [ ] Security checks passed

## 📊 Performance Benchmarks

- **Page Load Time**: < 2 seconds
- **Booking Creation**: < 1 second
- **Database Queries**: < 500ms average
- **Email Delivery**: < 5 seconds
- **Concurrent Users**: Support 100+ simultaneous

---

