FROM tensorflow/serving:2.6.0
ENV MODEL_NAME=my_model
COPY  .  /models/$MODEL_NAME/1/
EXPOSE 8500
EXPOSE 8501
CMD ["tensorflow_model_server","--port=8500", "--rest_api_port=8501", "--model_name=my_model", "--model_base_path=/models/my_model"]