from openwakeword.model import Model

print("Loading ONNX model...")

model = Model(inference_framework="onnx")

print("Loaded successfully!")
print(model.models.keys())