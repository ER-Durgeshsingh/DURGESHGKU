import smtplib
import streamlit as st
from email.message import EmailMessage
from datetime import datetime, timedelta

from src.database.db import create_attendance
from src.database.config import supabase


def _send_gmail(to_email, subject, body):
    try:
        gmail_address = st.secrets["GMAIL_ADDRESS"]
        gmail_app_password = st.secrets["GMAIL_APP_PASSWORD"]

        msg = EmailMessage()
        msg["From"] = gmail_address
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_address, gmail_app_password)
            smtp.send_message(msg)

        return True

    except Exception as e:
        st.error(f"Gmail Error: {e}")
        return False


def show_attendance_result(df, logs):
    st.write("Please review attendance before confirming.")
    st.dataframe(df, hide_index=True, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Discard",
            use_container_width=True,
            key="attendance_result_discard_btn"
        ):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()

    with col2:
        if st.button(
            "Confirm & Save",
            use_container_width=True,
            type="primary",
            key="attendance_result_confirm_save_btn"
        ):
            try:
                now = datetime.now()
                valid_logs = []

                for log in logs:
                    student_id = log["student_id"]
                    subject_id = log["subject_id"]

                    thirty_min_ago = (now - timedelta(minutes=30)).isoformat()

                    old = (
                        supabase.table("attendance_logs")
                        .select("*")
                        .eq("student_id", student_id)
                        .eq("subject_id", subject_id)
                        .gte("timestamp", thirty_min_ago)
                        .execute()
                    )

                    if not old.data:
                        valid_logs.append(log)

                if not valid_logs:
                    st.toast("Attendance already marked")
                    st.session_state.attendance_images = []
                    st.session_state.voice_attendance_results = None
                    st.rerun()

                create_attendance(valid_logs)

                today_start = now.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0
                ).isoformat()

                for log in valid_logs:
                    res = (
                        supabase.table("students")
                        .select("name,parent_email")
                        .eq("student_id", log["student_id"])
                        .single()
                        .execute()
                    )

                    sub = (
                        supabase.table("subjects")
                        .select("name,subject_code")
                        .eq("subject_id", log["subject_id"])
                        .single()
                        .execute()
                    )

                    student = res.data
                    subject = sub.data

                    if student and student.get("parent_email"):

                        email_check = (
                            supabase.table("attendance_logs")
                            .select("*")
                            .eq("student_id", log["student_id"])
                            .eq("subject_id", log["subject_id"])
                            .gte("timestamp", today_start)
                            .execute()
                        )

                        if len(email_check.data) > 1:
                            continue

                        status = "PRESENT" if log.get("is_present") else "ABSENT"

                        subject_name = subject.get("name", "Unknown Subject") if subject else "Unknown Subject"
                        subject_code = subject.get("subject_code", "N/A") if subject else "N/A"
                        attendance_date = log.get(
                            "timestamp",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )

                        body = f"""
Dear Parent,

Your child {student.get('name', 'Student')} was marked {status}.

Subject: {subject_name} ({subject_code})
Date: {attendance_date}

Regards,
AI Attendance System
DURGESHWAR KUMAR SINGH
Guru Kashi University
"""

                        _send_gmail(
                            student["parent_email"],
                            "Attendance Notification",
                            body
                        )

                st.toast("Attendance taken")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.rerun()

            except Exception as e:
                st.error(f"Sync failed! {e}")


@st.dialog("Attendance Reports")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)