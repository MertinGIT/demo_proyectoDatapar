import os
MODEL_PATH = "C:/models/llama-2-7b.Q2_K.gguf"
print(f"Comprobando si existe: {MODEL_PATH}")
print(f"Existe: {os.path.exists(MODEL_PATH)}")