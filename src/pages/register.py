import streamlit as st
from pages.create_resume import show_create_resume_page
from psycopg2.extras import RealDictCursor
from passlib.hash import bcrypt
from repositories.connector import get_connection

def register_candidate(user_id, email, phone, show_phone):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO Candidates (user_id, email, phone, show_phone)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, email, phone, show_phone)
                )
                conn.commit()
                st.success("Регистрация кандидата прошла успешно!")
    except Exception as e:
        st.error(f"Ошибка: {e}")

def register_employer(user_id, email, phone, show_phone):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO Employers (user_id, email, phone, show_phone)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, email, phone, show_phone)
                )
                conn.commit()
                #st.success("Регистрация кандидата прошла успешно!")
    except Exception as e:
        st.error(f"Ошибка: {e}")


# Регистрация пользователя
def register_user(username, password, role, email, phone, show_phone):
    password_hash = bcrypt.hash(password)
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO Users (username, password_hash, role)
                    VALUES (%s, %s, %s)
                    RETURNING user_id
                    """,
                    (username, password_hash, role)
                )
                user_id = cur.fetchone()[0]
                st.session_state.user_id = user_id
                conn.commit()
                if role == "candidate":
                    register_candidate(user_id, email, phone, show_phone)
                elif role == "employer":
                    register_employer(user_id, email, phone, show_phone)
                st.success("Регистрация прошла успешно!")
    except Exception as e:
        st.error(f"Ошибка: {e}")

def show_register_page():
    role = st.session_state.get("role")
    st.subheader("Регистрация пользователя")
    username = st.text_input("Логин")
    email = st.text_input("Email")
    phone = st.text_input("Телефон")
    show_phone = st.checkbox("Показывать телефон")
    password = st.text_input("Пароль", type="password")
    password_confirm = st.text_input("Подтвердите пароль", type="password")
    #role = st.selectbox("Роль", ["candidate", "employer", "admin"])
    if st.button("Зарегистрироваться"):
        if username and password and role:
            if password != password_confirm:
                st.error("Пароли не совпадают!")
            else:
                register_user(username, password, role, email, phone, show_phone)
                if role == "candidate":
                    st.session_state.page = "register_candidate"
                elif role == "employer":
                    st.session_state.page = "register_employer"
        else:
            st.warning("Заполните все поля!")
        if st.session_state.get("page") == "register_candidate":
            st.switch_page("pages/create_resume.py")
        elif st.session_state.get("page") == "register_employer":
            st.switch_page("pages/view_resumes.py")
if __name__ == "__main__":
    show_register_page()
