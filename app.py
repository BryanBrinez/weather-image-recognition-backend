from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import os

# Crear la aplicación Flask
app = Flask(__name__)

# Habilitar CORS
CORS(app)

# Cargar el modelo entrenado
MODEL_PATH = "modelo.keras"
try:
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Error al cargar el modelo: {e}")

# Etiquetas de las categorías
CATEGORIES = ['dew', 'rain', 'rime', 'rainbow', 'hail', 'frost', 'snow', 'fogsmog', 'glaze', 'sandstorm', 'lightning']

@app.route('/predict', methods=['POST'])
def predict():
    # Verificar que se envió una imagen
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ninguna imagen"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    try:
        # Leer la imagen enviada
        image = tf.io.decode_image(file.read(), channels=3, expand_animations=False)
        
        # Verificar que la imagen es válida
        if image is None:
            return jsonify({"error": "La imagen no es válida"}), 400

        image = tf.image.resize(image, [100, 100]) / 255.0
        image = tf.expand_dims(image, axis=0)

        # Realizar la predicción
        predictions = model.predict(image)
        predicted_index = np.argmax(predictions)
        predicted_label = CATEGORIES[predicted_index]

        return jsonify({
            "prediction": predicted_label,
            "confidence": float(np.max(predictions))
        })
    
    except Exception as e:
        # Manejo de errores durante el procesamiento de la imagen o la predicción
        return jsonify({"error": f"Error en el procesamiento de la imagen: {str(e)}"}), 500

if __name__ == '__main__':
    # Asegúrate de que el puerto y host son correctos
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error al iniciar la aplicación Flask: {str(e)}")
