from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)

# Train the model
results = model.train(data="/home/pi/pinball/dataset/pinball.v1i.yolov8/data.yaml", epochs=100, imgsz=640, batch=8, device=0)
