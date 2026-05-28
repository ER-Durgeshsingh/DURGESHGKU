import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.config import supabase
from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject
)
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    if "show_profile_editor" not in st.session_state:
        st.session_state.show_profile_editor = False

    profile_photo_url = student_data.get("profile_photo_url")
    photo_uploaded = student_data.get("photo_uploaded", False)

    left_col, photo_col, right_col = st.columns(
        [3.8, 1.2, 3],
        vertical_alignment='center',
        gap='medium'
    )

    with left_col:
        header_dashboard()

    with photo_col:
        if profile_photo_url:
            st.image(profile_photo_url, width=145)
        else:
            st.image(
                "https://cdn-icons-png.flaticon.com/512/149/149071.png",
                width=120
            )

        if not photo_uploaded:
            uploaded_photo = st.file_uploader(
                "Upload Photo",
                type=["jpg", "jpeg", "png"],
                key="student_profile_photo_upload"
            )

            if uploaded_photo:
                if st.button(
                    "Save Photo",
                    type="primary",
                    key="save_student_photo_btn"
                ):
                    try:
                        file_bytes = uploaded_photo.getvalue()
                        file_ext = uploaded_photo.name.split(".")[-1]
                        file_path = f"student_photos/{student_id}.{file_ext}"

                        supabase.storage.from_("student-photos").upload(
                            file_path,
                            file_bytes,
                            {"content-type": uploaded_photo.type}
                        )

                        public_url = supabase.storage.from_(
                            "student-photos"
                        ).get_public_url(file_path)

                        supabase.table("students").update({
                            "profile_photo_url": public_url,
                            "photo_uploaded": True
                        }).eq("student_id", student_id).execute()

                        student_data["profile_photo_url"] = public_url
                        student_data["photo_uploaded"] = True
                        st.session_state.student_data = student_data

                        st.success("Profile photo uploaded successfully.")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Photo upload failed: {e}")
        else:
            st.caption("📸 Photo locked.")

    with right_col:
        top_col1, top_col2 = st.columns([5, 1])

        with top_col1:
            st.subheader(f"Welcome,\n{student_data.get('name', 'Student')}")

        with top_col2:
            if st.button("✏️", key="open_profile_edit_btn", help="Edit Profile"):
                st.session_state.show_profile_editor = not st.session_state.show_profile_editor
                st.rerun()

        if st.button(
            "Logout",
            type='secondary',
            key='student_logout_btn',
            shortcut="control+backspace"
        ):
            st.session_state['is_logged_in'] = False
            if "show_profile_editor" in st.session_state:
                del st.session_state.show_profile_editor
            del st.session_state.student_data
            st.rerun()

    st.space()

    current_name = student_data.get("name", "")
    current_email = student_data.get("parent_email", "")
    update_count = student_data.get("profile_update_count", 0) or 0

    profile_locked = update_count >= 2
    remaining_updates = max(0, 2 - update_count)

    if st.session_state.show_profile_editor:
        with st.container(border=True):
            st.markdown("### 👤 Student Profile")
            st.caption("Manage your name and parent email for attendance notifications.")

            st.info(f"Profile update remaining: {remaining_updates}")

            profile_col1, profile_col2 = st.columns(2)

            with profile_col1:
                updated_name = st.text_input(
                    "Student Name",
                    value=current_name,
                    disabled=profile_locked,
                    key="update_student_name"
                )

            with profile_col2:
                updated_email = st.text_input(
                    "Parent Email",
                    value=current_email,
                    disabled=profile_locked,
                    key="update_parent_email"
                )

            if profile_locked:
                st.success("✅ Profile update limit completed. Details are locked for security.")
            else:
                st.caption("Note: Student profile can be updated only 2 times.")

            btn_col1, btn_col2 = st.columns([1, 3])

            with btn_col1:
                if st.button(
                    "💾 Save",
                    type="primary",
                    key="save_student_details_btn",
                    disabled=profile_locked
                ):
                    if profile_locked:
                        st.warning("Profile can be updated only 2 times.")
                    else:
                        if not updated_name:
                            st.warning("Please enter student name.")
                            return

                        if not updated_email:
                            st.warning("Please enter parent email.")
                            return

                        update_data = {
                            "name": updated_name,
                            "parent_email": updated_email,
                            "profile_update_count": update_count + 1
                        }

                        supabase.table("students").update(update_data).eq(
                            "student_id",
                            student_id
                        ).execute()

                        st.success("Profile details saved successfully.")
                        student_data.update(update_data)
                        st.session_state.student_data = student_data
                        st.rerun()

            with btn_col2:
                if st.button("Close", key="close_profile_editor_btn"):
                    st.session_state.show_profile_editor = False
                    st.rerun()

    st.space()

    c1, c2 = st.columns(2)

    with c1:
        st.header('Your Enrolled Subjects')

    with c2:
        if st.button(
            'Enroll in Subject',
            type='primary',
            width='stretch',
            key='student_open_enroll_dialog_btn'
        ):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}

        stats_map[sid]['total'] += 1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    cols = st.columns(2)

    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']

        stats = stats_map.get(sid, {"total": 0, "attended": 0})

        def unenroll_button(sub=sub, sid=sid):
            if st.button(
                "Unenroll from this course",
                type='tertiary',
                width='stretch',
                icon=':material/delete_forever:',
                key=f"student_unenroll_{sid}",
            ):
                unenroll_student_to_subject(student_id, sid)
                st.toast(f'Unenrolled from {sub["name"]} successfully!')
                st.rerun()

        with cols[i % 2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=unenroll_button,
            )

    footer_dashboard()


def student_screen():

    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Go back to Home",
            type='secondary',
            key='student_back_home_btn',
            shortcut="control+backspace"
        ):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using FaceID', text_alignment='center')
    st.space()
    st.space()

    show_registration = False

    photo_source = st.camera_input(
        "Position your face in the center",
        key="student_face_login_camera"
    )

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner('AI is scanning..'):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning('Face not found!')

            elif num_faces > 1:
                st.warning('Multiple faces found')

            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()

                    student = next(
                        (s for s in all_students if s['student_id'] == student_id),
                        None
                    )

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f'Welcome Back {student.get("name", "Student")}')
                        time.sleep(1)
                        st.rerun()

                else:
                    st.info('Face not recognized! You might be a new student!')
                    show_registration = True

    if show_registration:
        with st.container(border=True):
            st.header('Register new Profile')

            new_name = st.text_input(
                "Enter your name",
                placeholder='E.g. Durgeshwar Kumar',
                key="student_register_name"
            )

            student_roll_number = st.text_input(
                "University Roll Number",
                placeholder="2023BCSE001",
                key="student_roll_number"
            )

            parent_email = st.text_input(
                "Parent Email",
                placeholder="abc@gmail.com",
                key="parent_email"
            )

            st.subheader('Optional : Voice Enrollment')
            st.info("Enroll your voice for voice-only attendance")

            audio_data = None

            try:
                audio_data = st.audio_input(
                    'Record a short phrase like I am present, My name is Akash.',
                    key='student_register_voice_audio'
                )
            except Exception:
                st.error('Audio Data failed!')

            if st.button(
                'Create Account',
                type='primary',
                key='student_create_account_btn'
            ):

                if not new_name:
                    st.warning('Please enter your name!')
                    return

                if not student_roll_number:
                    st.warning('Please enter university roll number!')
                    return

                if not parent_email:
                    st.warning('Please enter parent email!')
                    return

                with st.spinner('Creating profile..'):
                    img = np.array(Image.open(photo_source))
                    encodings = get_face_embeddings(img)

                    if encodings:
                        face_emb = encodings[0].tolist()
                        voice_emb = None

                        if audio_data:
                            voice_emb = get_voice_embedding(audio_data.read())

                        response_data = create_student(
                            new_name,
                            student_roll_number=student_roll_number,
                            parent_email=parent_email,
                            face_embedding=face_emb,
                            voice_embedding=voice_emb
                        )

                        if response_data:
                            train_classifier()
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = response_data[0]
                            st.toast(f'Profile Created! Hi {new_name}!')
                            time.sleep(1)
                            st.rerun()

                    else:
                        st.error('Could not capture your facial features for registration')

    footer_dashboard()