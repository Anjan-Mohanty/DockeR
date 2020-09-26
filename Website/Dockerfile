FROM python:3.8.5
COPY . /usr/app/
EXPOSE 8501
WORKDIR /usr/app/
RUN pip3 install -r requirements.txt
CMD streamlit run st_app.py