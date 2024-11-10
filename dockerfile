# 確定python版本來讓docker建立時載入
FROM python:3.9.12

# --- 在這邊設定和python有關的環境變數 ---

# 是否啟用緩衝載入
ENV PYTHONUNBUFFERED 1

# ===================================

# 建立資料夾作為部署用容器
RUN mkdir /code
# 指定資料夾為部署docker工作用
WORKDIR /code

# 更新 pip
RUN pip install pip -U

# 把 requirements.txt 檔案複製進容器裡
ADD requirements.txt /code/

# 在容器裡安裝plugin建立環境
RUN pip install -r requirements.txt

# 把寫完的django project整包帶進去容器裡
ADD . /code/