# CSEClass AI Attendance - Setup & Live Deployment Guide

## 1. Supabase setup

1. Open Supabase Dashboard.
2. Create a new project.
3. Go to **SQL Editor**.
4. Open `supabase/schema.sql` from this project.
5. Copy all SQL and click **Run**.
6. Go to **Project Settings > API**.
7. Copy `Project URL` and `anon public key`.
8. Paste them in `.streamlit/secrets.toml`.

---

## 2. Gmail OTP setup

1. Open your Google Account.
2. Enable 2-Step Verification.
3. Search **App Passwords**.
4. Create an app password for Mail.
5. Paste Gmail and app password in `.streamlit/secrets.toml`:

```toml
GMAIL_ADDRESS = "yourgmail@gmail.com"
GMAIL_APP_PASSWORD = "your16digitapppassword"
```

If Gmail is not configured, OTP still works in local development by showing a DEV OTP warning on screen.

---

## 3. Student Photo Upload Setup

### Create Supabase Storage Bucket

1. Open **Supabase Dashboard**.
2. Go to **Storage**.
3. Click **New Bucket**.
4. Bucket name:

```text
student-photos
```

5. Enable:

```text
Public Bucket = ON
```

6. Create bucket.

### Add Storage Policies

Open **SQL Editor** and run:

```sql
CREATE POLICY "Allow public upload to student photos"
ON storage.objects
FOR INSERT
TO anon, authenticated
WITH CHECK (bucket_id = 'student-photos');

CREATE POLICY "Allow public update student photos"
ON storage.objects
FOR UPDATE
TO anon, authenticated
USING (bucket_id = 'student-photos')
WITH CHECK (bucket_id = 'student-photos');
```

### Student Photo Features

* Student can upload profile photo after registration.
* Profile photo appears between logo and welcome section.
* Photo upload allowed only once.
* Photo is securely stored in Supabase Storage.

---

## 4. Attendance Email Notification Setup

### Parent Attendance Email Alerts

The system automatically sends attendance emails to parents.

### Features

* Present/Absent email notification.
* Subject name and subject code included.
* Attendance date included.
* Same subject email sent only once per day.
* No email error if parent email is missing.

### Duplicate Attendance Protection

* Same student attendance cannot be marked twice within 30 minutes for same subject.
* Duplicate students are skipped automatically.
* Other students' attendance still gets marked successfully.

---

## 5. Student Profile Update Rules

### Profile Security Features

* Student can update profile only 2 times.
* Parent email can also be updated only 2 times.
* After limit completion, profile becomes locked.
* Remaining update count is shown in dashboard.

---

## 6. Run locally in VS Code

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 7. Deploy on Streamlit Cloud

1. Push project to GitHub.

2. Open Streamlit Cloud.

3. New app > select GitHub repository.

4. Main file path: `app.py`.

5. In Streamlit Cloud app settings > Secrets, paste:

```toml
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_anon_key"

GMAIL_ADDRESS = "yourgmail@gmail.com"
GMAIL_APP_PASSWORD = "your_app_password"
```

6. Deploy.

---

# 8. New Features Added

## Authentication

* Teacher registration with Gmail/email.
* Gmail OTP login.
* Forgot password with Gmail OTP.
* Student face login system.
* Voice attendance support.

## Attendance System

* AI Face Recognition Attendance.
* Voice Recognition Attendance.
* Auto attendance analytics.
* Duplicate attendance protection.
* Subject-wise attendance tracking.
* Daily attendance email alerts to parents.

## Reports & Export

* Attendance Excel export.
* Monthly attendance PDF export.
* Attendance analytics dashboard.
* Month-wise attendance trend.
* Attendance percentage tracking.

## Student Dashboard

* Student profile photo upload.
* Editable profile with security limits.
* Subject enrollment system.
* Attendance statistics cards.

## Admin Features

* Admin dashboard.
* Low attendance alerts below 75%.
* Subject management.
* Student enrollment management.

## Security Features

* OTP verification.
* Parent email validation.
* Profile update limits.
* Secure Supabase storage integration.
* One-time photo upload system.



# Future Advanced Features for CSEClass AI Attendance System

## 1. QR Code Attendance

* Teacher subject-wise QR generate kare
* Student scan karke attendance mark kare
* Time-limited QR for security

---

## 2. Live Camera Classroom Detection

* Classroom camera se automatic multiple face detection
* Entire class attendance automatically
* Proxy detection

---

## 3. Geo-Location Attendance

* Attendance only inside college campus
* GPS verification
* Fake attendance prevention

---

## 4. Anti-Spoofing AI Security

* Detect fake photos/videos
* Blink detection
* Real face verification

---

## 5. Student Mobile App

* Android app
* Student attendance history
* Notifications
* Leave request system

---

## 6. Teacher Mobile App

* Instant attendance marking
* Subject management
* Attendance analytics
* Parent notification controls

---

## 7. Leave Management System

* Student leave request
* Medical leave upload
* Teacher approval/rejection
* Leave history

---

## 8. Timetable Integration

* Automatic subject detection based on time
* Auto-open attendance session
* Faculty timetable management

---

## 9. AI Attendance Insights

* Weak attendance prediction
* Risk students detection
* Attendance performance charts
* Monthly AI analysis

---

## 10. SMS + WhatsApp Notification

* Parent WhatsApp alerts
* SMS alerts
* Daily summary reports

---

## 11. Multi-Role Dashboard

### Roles

* Admin
* Teacher
* Student
* HOD
* Principal

Each role gets separate dashboard.

---

## 12. Attendance Correction Request

* Student can request correction
* Teacher approve/reject
* Full audit log

---

## 13. Dark/Light Theme

* User theme switch
* Modern UI
* Responsive design

---

## 14. Classroom Analytics

* Most absent students
* Subject-wise attendance charts
* Daily/monthly reports
* Heatmap analytics

---

## 15. Cloud Backup System

* Automatic database backup
* Export all attendance
* Disaster recovery support

---

## 16. AI Voice Assistant

Example:

* "Show today's attendance"
* "Export AI/ML report"
* "Open attendance analytics"

---

## 17. Face + Voice Dual Verification

* Attendance only when both match
* Higher security
* Anti-proxy system

---

## 18. Attendance Certificate Generator

* Auto PDF generation
* Semester attendance report
* Student-wise certificates

---

## 19. Bulk Student Import

* Excel upload
* CSV student import
* Auto enrollment

---

## 20. Real-Time Notifications

* Attendance marked popup
* Low attendance alerts
* Teacher announcements
* Live updates
