# dog_identification.py
import tensorflow as tf
import tensorflow_hub as hub

IMG_SIZE = 224
INPUT_SHAPE = [None, IMG_SIZE, IMG_SIZE, 3]
OUTPUT_SHAPE = 120  # Set to your number of breeds
MODEL_URL = "https://kaggle.com/models/google/mobilenet-v2/TensorFlow2/100-224-feature-vector/1"


def create_model(input_shape=INPUT_SHAPE, output_shape=OUTPUT_SHAPE, model_url=MODEL_URL):
    print("Building model with:", model_url)

    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=input_shape[1:]),
        tf.keras.layers.Lambda(lambda x: hub.KerasLayer(model_url)(x)),
        tf.keras.layers.Dense(units=output_shape, activation="softmax")
    ])

    model.compile(
        loss=tf.keras.losses.CategoricalCrossentropy(),
        optimizer=tf.keras.optimizers.Adam(),
        metrics=["accuracy"]
    )

    return model
