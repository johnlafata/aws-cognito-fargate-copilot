FROM public.ecr.aws/docker/library/python:3.13.1-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# setup environment 
RUN  pip install authlib werkzeug flask requests waitress
# Copy the rest of the application code to the working directory
COPY app .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the Gradio app
CMD ["python", "main.py"]
