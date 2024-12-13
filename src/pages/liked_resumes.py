import streamlit as st
from psycopg2.extras import RealDictCursor
from repositories.connector import get_connection

def get_liked_resumes(employer_id):
    query = """
        SELECT lr.liked_date, rs.resume_id, rs.user_id, rs.last_modified, rs.age, rs.experience, rs.city, 
               rs.nearby_metro, rs.employment_type, rs.remote_work_possible, rs.profession_name,
               rs.skills, rs.description, u.username AS candidate_username
        FROM LikedResumes lr
        JOIN ResumeSearch rs ON lr.user_id = rs.user_id
        JOIN Users u ON rs.user_id = u.user_id
        WHERE lr.employer_id = %s
        ORDER BY lr.liked_date DESC;
    """
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (employer_id,))
                return cur.fetchall()
    except Exception as e:
        st.error(f"Ошибка при получении понравившихся резюме: {e}")
        return []


# Страница для отображения понравившихся резюме
def show_liked_resumes_page():
    st.page_link("pages/edit_employer_data.py", label="Изменить данные аккаунта")
    st.page_link("pages/liked_resumes.py", label="Понравившиеся резюме")
    st.page_link("pages/view_resumes.py", label="Посмотреть другие резюме")
    st.title("Понравившиеся резюме")

    employer_id = st.session_state.get("user_id")
    if not employer_id or st.session_state.get("role") != "employer":
        st.warning("Только работодатели могут просматривать понравившиеся резюме.")
        return

    liked_resumes = get_liked_resumes(employer_id)

    if not liked_resumes:
        st.info("У вас пока нет понравившихся резюме.")
        return

    # Отображение понравившихся резюме
    i = 0
    for resume in liked_resumes:
        with st.container():
            st.markdown(f"### {resume['profession_name']}")
            st.markdown(f"**Дата добавления в понравившиеся:** {resume['liked_date']}")
            st.markdown(f"**Возраст:** {resume['age']} | **Опыт:** {resume['experience']} лет")
            st.markdown(f"**Город:** {resume['city']} | **Метро:** {resume['nearby_metro']}")
            st.markdown(f"**Тип занятости:** {resume['employment_type']} | **Удаленная работа:** {'Да' if resume['remote_work_possible'] else 'Нет'}")
            st.markdown(f"**Последнее изменение резюме:** {resume['last_modified']}")
            st.markdown(f"**Описание:** {resume['description']}")
            
            skills = resume.get('skills', [])
            if skills:
                st.markdown(f"**Навыки:** {', '.join(skills)}")
            else:
                st.markdown("**Навыки:** Не указаны")
            to_resume = st.button(f"Узнать подробнее", key=f"button_{i}", type="primary")
            i = i + 1
            if to_resume:
                st.session_state['selected_resume'] = resume
                st.switch_page("pages/view_resume_details.py")
            st.markdown("---")

# Запуск страницы
if __name__ == "__main__":
    show_liked_resumes_page()
