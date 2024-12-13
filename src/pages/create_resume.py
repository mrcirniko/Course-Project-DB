import streamlit as st
from services.edit_resume_service import add_resume_to_db, add_work_experience_to_db, add_skills_to_db, get_professions

def show_create_resume_page():
    if 'user_id' not in st.session_state:
        st.error("Необходимо авторизоваться")
        return

    st.title("Резюме еще не создано")
    st.write("Для создания резюме сначала укажите основные данные")
    
    user_id = st.session_state['user_id']  # Получаем идентификатор пользователя из сессии

    # Загружаем список профессий для селектора
    try:
        professions = get_professions()
    except Exception as e:
        st.error(f"Ошибка при загрузке профессий: {e}")
        return

    profession_options = [profession[1] for profession in professions]
    profession_id = st.selectbox("Профессия", profession_options)
    
    # Получаем ID выбранной профессии
    if profession_id in profession_options:
        profession_id = professions[profession_options.index(profession_id)][0]
    else:
        st.error("Профессия не найдена!")
        return

    age = st.number_input("Возраст", min_value=18, max_value=100)
    experience = st.number_input("Опыт работы (в годах)", min_value=0)
    city = st.text_input("Город проживания")
    nearby_metro = st.text_input("Ближайшее метро")
    employment_type = st.selectbox("Тип занятости", ["Полная", "Частичная", "Проектная", "Стажировка", "Волонтёрская"])
    description = st.text_area("Описание")
    remote_work_possible = st.checkbox("Готовность работать удаленно")

    if st.button("Сохранить резюме"):
        try:
            resume_id = add_resume_to_db(user_id, profession_id, age, experience, city, nearby_metro, employment_type, description, remote_work_possible)
            st.session_state['resume_id'] = resume_id
            st.success("Резюме успешно сохранено!")
        except Exception as e:
            st.error(f"Ошибка при сохранении резюме: {e}")
        
    # Добавление опыта работы
    st.subheader("Опыт работы")
    with st.expander("Добавить место работы"):
        workplace_name = st.text_input("Название компании")
        workplace_description = st.text_area("Описание места работы (необязательно)")
        position = st.text_input("Должность")
        start_date = st.date_input("Дата начала работы")
        end_date = st.date_input("Дата окончания работы (оставьте пустым, если работаете сейчас)")
        responsibilities = st.text_area("Обязанности")
        
        if st.button("Добавить опыт работы"):
            try:
                if workplace_name and position and start_date:
                    add_work_experience_to_db(user_id, workplace_name, workplace_description, position, start_date, end_date, responsibilities)
                    st.success("Опыт работы добавлен!")
            except Exception as e:
                st.error(f"Ошибка при добавлении опыта работы: {e}")

    # Добавление профессиональных навыков
    st.subheader("Профессиональные навыки")
    skill_input = st.text_input("Добавьте навыки (через запятую)")
    if st.button("Сохранить навыки"):
        skills = skill_input.split(',')
        skills = [skill.strip() for skill in skills]
        try:
            resume_id = st.session_state.get('resume_id')  # Получаем ID резюме из сессии
            if resume_id:
                add_skills_to_db(skills, resume_id)
                st.success("Навыки сохранены!")
            else:
                st.error("Резюме не найдено!")
        except Exception as e:
            st.error(f"Ошибка при сохранении навыков: {e}")

if __name__ == "__main__":
    show_create_resume_page()
