import streamlit as st
from repositories.connector import get_connection
from psycopg2.extras import RealDictCursor

def get_candidate_contact(user_id):
    """Получает контактные данные кандидата."""
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                SELECT c.email, c.phone, c.show_phone
                FROM Candidates c
                WHERE c.user_id = %s;
                """
                cur.execute(query, (user_id,))
                return cur.fetchone()
    except Exception as e:
        st.error(f"Ошибка при получении контактных данных кандидата: {e}")
        return None

def show_resume_details_page():
    st.title("Детали резюме")

    if 'selected_resume' not in st.session_state or not st.session_state['selected_resume']:
        st.warning("Резюме не выбрано.")
        st.stop()

    resume = st.session_state['selected_resume']

    st.markdown(f"**Дата последнего редактирования:** {resume['last_modified']}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Возраст:** {resume['age']}")
        st.markdown(f"**Опыт работы (в годах):** {resume['experience']}")
        st.markdown(f"**Специальность:** {resume['profession_name']}")
    with col2:
        st.markdown(f"**Город:** {resume['city']}")
        st.markdown(f"**Ближайшее метро:** {resume['nearby_metro']}")
        st.markdown(f"**Тип занятости:** {resume['employment_type']}")
        st.markdown(f"**Готовность работать удаленно:** {'Да' if resume['remote_work_possible'] else 'Нет'}")
    
    if resume['description'] != "":
        st.markdown(f"**Обо мне:** {resume['description']}")
    # Скиллы
    skills = resume.get('skills', []) or []
    if skills:
        st.markdown(f"**Профессиональные навыки:** {', '.join(skills)}")
    else:
        st.markdown("**Профессиональные навыки:** Не указаны")

    # Предыдущие места работы
    positions = resume.get('positions', []) or []
    if positions:
        st.markdown(f"**Прошлые места работы (должности):** {', '.join(positions)}")
    else:
        st.markdown("**Прошлые места работы:** Не указаны")

    # Получение контактной информации
    contact_info = get_candidate_contact(resume['user_id'])

    if contact_info:
        st.markdown("### Контактная информация")
        st.markdown(f"**Email:** {contact_info['email']}")
        if contact_info['show_phone']:
            st.markdown(f"**Телефон:** {contact_info['phone']}")
        else:
            st.markdown("**Телефон:** Скрыт пользователем")

    # Кнопка возврата
    if st.button("Вернуться к списку резюме"):
        st.session_state['selected_resume'] = None
        #st.experimental_rerun()
        st.switch_page("pages/view_resumes.py")

# Запуск страницы
if __name__ == "__main__":
    show_resume_details_page()