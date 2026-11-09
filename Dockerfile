# Docker image for the AI tutor app on SciLifeLab Serve
FROM python:3.13-slim

# SciLifeLab Serve requires a non-root user with user id 1000
ENV USER=username
ENV HOME=/home/$USER
RUN useradd -m -u 1000 $USER

# The start script must be in the working directory
WORKDIR $HOME/app

COPY requirements.txt $HOME/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py $HOME/app/app.py
COPY start-script.sh $HOME/app/start-script.sh

RUN chmod +x start-script.sh && chown -R $USER:$USER $HOME

# Do not send usage statistics from Gradio
ENV GRADIO_ANALYTICS_ENABLED=False

USER $USER
EXPOSE 7860

ENTRYPOINT ["./start-script.sh"]
