from ultralytics import YOLO

# Load a model
model = YOLO('yolov8n.yaml')  # build a new model from YAML
# model = YOLO(r'C:\projectyolo\runs\detect\train17\weights\best17.pt')  # load a pretrained model (recommended for training)
# model = YOLO('yolov8n.yaml').load(r'C:\projectyolo\runs\detect\train17\weights\best17.pt')  # build from YAML and transfer weights
# Use the model
model.train(data="config.yml", epochs=300, batch=4)  # train the model
# metrics = model.val()
# path = model.export(format="onnx")