from ultralytics import YOLO

# Load a model
model = YOLO('yolov8n.yaml')  # build a new model from YAML
model = YOLO(r'.\runs\detect\train4\weights\best4.pt')  # load a pretrained model (recommended for training)
model = YOLO('yolov8n.yaml').load(r'.\runs\detect\train4\weights\best4.pt')  # build from YAML and transfer weights
# Use the model
model.train(data="config.yml", epochs=100, batch=4, learning_rate=0.0005)  # train the model
# metrics = model.val()
path = model.export(format="onnx")