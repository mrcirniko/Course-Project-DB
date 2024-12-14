import streamlit as st
from repositories.connector import get_connection
from psycopg2.extras import RealDictCursor
from streamlit_tags import st_tags
from services.edit_resume_service import get_professions
import streamlit as st
from psycopg2.extras import RealDictCursor
from passlib.hash import bcrypt
from contextlib import contextmanager
from settings import DB_CONFIG, POOL_MIN_CONN, POOL_MAX_CONN
import psycopg2.pool
import atexit
from pages.create_resume import show_create_resume_page
from streamlit_option_menu import option_menu

from pages.login import show_login_page
from pages.register import show_register_page

# Функция для получения списка профессиональных навыков (для отображения в интерфейсе)
def get_skills():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT skill_name FROM Skills")
                skills = cur.fetchall()
                return [skill[0] for skill in skills]
    except Exception as e:
        raise Exception(f"Ошибка при получении навыков: {e}")

# Функция для получения всех резюме
def get_all_resumes(filters, sort_by):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                SELECT r.*, 
                       p.profession_name, 
                       array_agg(DISTINCT s.skill_name) FILTER (WHERE s.skill_name IS NOT NULL) AS skills,
                       array_agg(DISTINCT we.position) FILTER (WHERE we.position IS NOT NULL) AS positions
                FROM Resumes r
                JOIN Professions p ON r.profession_id = p.profession_id
                LEFT JOIN ResumeSkills rs ON r.resume_id = rs.resume_id
                LEFT JOIN Skills s ON rs.skill_id = s.skill_id
                LEFT JOIN WorkExperience we ON r.user_id = we.candidate_id
                """
                where_clauses = []
                values = []

                # Применяем фильтры
                if filters['age_min'] is not None:
                    where_clauses.append("r.age >= %s")
                    values.append(filters['age_min'])
                if filters['age_max'] is not None:
                    where_clauses.append("r.age <= %s")
                    values.append(filters['age_max'])
                if filters['experience_min'] is not None:
                    where_clauses.append("r.experience >= %s")
                    values.append(filters['experience_min'])
                if filters['experience_max'] is not None:
                    where_clauses.append("r.experience <= %s")
                    values.append(filters['experience_max'])
                if filters['profession']:
                    where_clauses.append("p.profession_name = %s")
                    values.append(filters['profession'])
                if filters['employment_type']:
                    where_clauses.append("r.employment_type = %s")
                    values.append(filters['employment_type'])

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                # Сортировка
                if sort_by == "Возраст":
                    query += " ORDER BY r.age"
                elif sort_by == "Опыт работы":
                    query += " ORDER BY r.experience"

                query += " GROUP BY r.resume_id, p.profession_name;"

                cur.execute(query, values)
                return cur.fetchall()
    except Exception as e:
        st.error(f"Ошибка при получении резюме: {e}")
        return []




def is_resume_liked(candidate_id, employer_id):
    query = """
        SELECT 1 
        FROM LikedResumes 
        WHERE user_id = %s AND employer_id = %s
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (candidate_id, employer_id))
            return cursor.fetchone() is not None

def add_to_liked_resumes(candidate_id, employer_id):
    query = """
        INSERT INTO LikedResumes (user_id, employer_id, liked_date)
        VALUES (%s, %s, CURRENT_DATE)
    """
    
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (candidate_id, employer_id))
            connection.commit()

# Страница для отображения всех резюме
def show_resumes_page():
    if 'role' in st.session_state and st.session_state.role == "candidate" and 'username' in st.session_state:
        st.page_link("pages/edit_candidate_data.py", label="Изменить данные аккаунта")
        st.page_link("pages/edit_resume.py", label="Ваше резюме")
        st.page_link("pages/view_resumes.py", label="Посмотреть другие резюме")

    elif 'role' in st.session_state and st.session_state.role == "employer" and 'username' in st.session_state:
        st.page_link("pages/edit_employer_data.py", label="Изменить данные аккаунта")
        st.page_link("pages/liked_resumes.py", label="Понравившиеся резюме")
        st.page_link("pages/view_resumes.py", label="Посмотреть другие резюме")

    st.title("Поиск резюме онлайн")
    try:
        professions = get_professions()
    except Exception as e:
        st.error(f"Ошибка при загрузке профессий: {e}")
        return

    try:
        skill_suggestions = get_skills()
    except Exception as e:
        st.error(f"Ошибка при загрузке навыков: {e}")
        return

    # Фильтры
    st.sidebar.header("Фильтры")
    age_min = st.sidebar.number_input("Минимальный возраст", min_value=18, max_value=100, step=1, value=18)
    age_max = st.sidebar.number_input("Максимальный возраст", min_value=18, max_value=100, step=1, value=100)
    experience_min = st.sidebar.number_input("Минимальный опыт (лет)", min_value=0, step=1, value=0)
    experience_max = st.sidebar.number_input("Максимальный опыт (лет)", min_value=0, step=1, value=50)
    profession_names = [""] + [profession[1] for profession in professions]
    profession = st.sidebar.selectbox("Профессия", options=profession_names)
    employment_types = ["Полная", "Частичная", "Проектная", "Стажировка", "Волонтёрская"]
    employment_type = st.sidebar.selectbox("Тип занятости", options=[""] + employment_types)
    print(skill_suggestions)
    skills = st_tags(
        label="",
        text="Введите навыки и нажмите Enter",
        value=[],
        suggestions=skill_suggestions,
        key="skill_tags"
    )

    sort_by = st.sidebar.selectbox("Сортировать по", options=["", "Возраст", "Опыт работы"])

    filters = {
        'age_min': age_min,
        'age_max': age_max,
        'experience_min': experience_min,
        'experience_max': experience_max,
        'profession': profession if profession else None,
        'employment_type': employment_type if employment_type else None,
        'skills': skills if skills else None
    }

    # Загружаем данные о резюме
    resumes = get_all_resumes(filters, sort_by)

    if not resumes:
        st.warning("Резюме не найдены.")
        return

    # Отображаем каждое резюме
    i = 0
    for resume in resumes:
        with st.container():
            st.markdown(f"### {resume['profession_name']}")
            st.markdown(f"**Дата последнего редактирования:** {resume['last_modified']}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Возраст:** {resume['age']}")
                st.markdown(f"**Опыт работы (в годах):** {resume['experience']}")
                st.markdown(f"**Готовность работать удаленно:** {'Да' if resume['remote_work_possible'] else 'Нет'}")
            with col2:
                st.markdown(f"**Город:** {resume['city']}")
                st.markdown(f"**Ближайшее метро:** {resume['nearby_metro']}")
                st.markdown(f"**Тип занятости:** {resume['employment_type']}")

            # Скиллы
            skills = resume.get('skills', []) or []
            if skills:
                st.markdown(f"**Навыки:** {', '.join(skills)}")
            else:
                st.markdown("**Навыки:** Не указаны")

            # Предыдущие места работы
            positions = resume.get('positions', []) or []
            if positions:
                st.markdown(f"**Прошлые места работы (должности):** {', '.join(positions)}")
            else:
                st.markdown("**Прошлые места работы:** Не указаны")
            col1, col2 = st.columns(2)
            with col1:
                to_resume = st.button(f"Узнать подробнее", key=f"button_{i}", type="primary")
                i = i + 1
                if to_resume:
                    st.session_state['selected_resume'] = resume
                    st.switch_page("pages/view_resume_details.py")
            with col2:
                like = st.button("", icon=":material/library_add:", key=f"button_{i}", type="primary")
                i += 1

                if like:
                    employer_id = st.session_state.get("user_id")
                    if not employer_id:
                        st.info("Только работодатели могут добавлять в понравившиеся.")
                    else:
                        try:
                            # Проверяем, есть ли запись в таблице
                            if is_resume_liked(resume['user_id'], employer_id):
                                st.info("Это резюме уже добавлено в понравившиеся.")
                            else:
                                add_to_liked_resumes(resume['user_id'], employer_id)
                                st.success("Добавлено в понравившиеся!")
                        except Exception as e:
                            st.error(f"Ошибка при добавлении: {e}")

            st.markdown("---")

# Запускаем страницу
if __name__ == "__main__":
    show_resumes_page()
