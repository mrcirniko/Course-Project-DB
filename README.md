## Курсовой проект по Базам данных


### Для запуска:  
Устанавливаем необходмые компоненты:
```
pip install -r .\requirements.txt
```
Копируем скрипты для создания базы данных
```
cd src
cp ./migrations/ddl.sql /tmp
cp ./migrations/dml.sql /tmp
```
Создаем базу данных:
```
sudo -i -u postgres
createdb mydb
psql -d mydb
\i /temp/ddl.sql
\i /temp/dml.sql
```
Запускаем проект:
```
streamlit run app.py
```
