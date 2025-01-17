import streamlit as st
from repositories.connector import get_connection
from psycopg2.extras import RealDictCursor
from passlib.hash import bcrypt

def update_candidate_data(user_id, username=None, email=None, phone=None, password=None, show_phone=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if username:
                cursor.execute(
                    """
                    UPDATE Users
                    SET username = %s
                    WHERE user_id = %s
                    """,
                    (username, user_id)
                )

            if password:
                password_hash = bcrypt.hash(password)
                cursor.execute(
                    """
                    UPDATE Users
                    SET password_hash = %s
                    WHERE user_id = %s
                    """,
                    (password_hash, user_id)
                )

            if email or phone or show_phone is not None:
                updates = []
                params = []
                if email:
                    updates.append("email = %s")
                    params.append(email)
                if phone:
                    updates.append("phone = %s")
                    params.append(phone)
                if show_phone is not None:
                    updates.append("show_phone = %s")
                    params.append(show_phone)

                params.append(user_id)
                cursor.execute(
                    f"""
                    UPDATE Candidates
                    SET {', '.join(updates)}
                    WHERE user_id = %s
                    """,
                    params
                )

            connection.commit()

def get_candidate_data(user_id):
    query = """
        SELECT u.username, c.email, c.phone, c.show_phone
        FROM Users u
        JOIN Candidates c ON u.user_id = c.user_id
        WHERE u.user_id = %s
    """
    
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (user_id,))
            return cursor.fetchone()

def show_edit_candidate_page():
    st.page_link("pages/edit_candidate_data.py", label="Изменить данные аккаунта")
    st.page_link("pages/edit_resume.py", label="Ваше резюме")
    st.page_link("pages/view_resumes.py", label="Посмотреть другие резюме")
    st.title("Редактировать данные профиля")

    # Получение user_id из сессии (или другой логики аутентификации)
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Вы не авторизованы.")
        return

    # Получаем текущие данные кандидата
    candidate_data = get_candidate_data(user_id)
    if not candidate_data:
        st.error("Не удалось загрузить данные пользователя.")
        return

    # Поля для редактирования
    username = st.text_input("Имя пользователя", candidate_data["username"])
    email = st.text_input("Email", candidate_data["email"])
    phone = st.text_input("Телефон", candidate_data["phone"])
    show_phone = st.checkbox("Показывать телефон", candidate_data["show_phone"])
    password = st.text_input("Новый пароль (если нужно изменить)", type="password")

    if st.button("Сохранить изменения"):
        try:
            update_candidate_data(
                user_id,
                username=username if username != candidate_data["username"] else None,
                email=email if email != candidate_data["email"] else None,
                phone=phone if phone != candidate_data["phone"] else None,
                password=password if password else None,
                show_phone=show_phone if show_phone != candidate_data["show_phone"] else None,
            )
            st.success("Данные успешно обновлены!")
        except Exception as e:
            st.error(f"Ошибка при обновлении данных: {e}")

# Для тестирования
if __name__ == "__main__":
    show_edit_candidate_page()
