from flask import Blueprint, request, jsonify
from pathlib import Path
from werkzeug.utils import secure_filename
import sqlite3
import uuid
import os
import numpy as np
import tensorflow as tf
from PIL import Image


# ============================================================
# BLUEPRINT
# ============================================================

prediction = Blueprint("prediction", __name__)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

UPLOAD_FOLDER = BASE_DIR / "backend" / "uploads"
DATABASE = BASE_DIR / "database" / "agroguard.db"
MODEL_PATH = BASE_DIR / "backend" / "agroguard_model.keras"

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading AgroGuard AI model...")

try:
    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    print("AgroGuard AI model loaded successfully!")

except Exception as error:

    print("MODEL LOADING ERROR:", error)

    model = None


# ============================================================
# CLASS NAMES
# ============================================================

class_names = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower() in ALLOWED_EXTENSIONS
    )


# ============================================================
# FORMAT DISEASE NAME
# ============================================================

def format_disease_name(class_name):

    # Remove crop prefix
    if "___" in class_name:

        crop, disease = class_name.split(
            "___",
            1
        )

    else:

        crop = "Unknown"
        disease = class_name

    disease = disease.replace(
        "_",
        " "
    )

    disease = disease.replace(
        "(",
        "("
    )

    return crop, disease


# ============================================================
# SEVERITY
# ============================================================

def calculate_severity(confidence, disease):

    if disease.lower() == "healthy":

        return "Healthy"

    if confidence >= 80:

        return "High"

    elif confidence >= 60:

        return "Medium"

    else:

        return "Low"


# ============================================================
# PREDICTION API
# ============================================================

@prediction.route(
    "/predict",
    methods=["POST"]
)
def predict():

    # --------------------------------------------------------
    # CHECK MODEL
    # --------------------------------------------------------

    if model is None:

        return jsonify({
            "success": False,
            "message": "AI model is not loaded"
        }), 500


    # --------------------------------------------------------
    # CHECK IMAGE
    # --------------------------------------------------------

    if "image" not in request.files:

        return jsonify({
            "success": False,
            "message": "No crop image received"
        }), 400


    image_file = request.files["image"]


    # --------------------------------------------------------
    # CHECK FILENAME
    # --------------------------------------------------------

    if image_file.filename == "":

        return jsonify({
            "success": False,
            "message": "Please select an image"
        }), 400


    # --------------------------------------------------------
    # CHECK EXTENSION
    # --------------------------------------------------------

    if not allowed_file(
        image_file.filename
    ):

        return jsonify({
            "success": False,
            "message": "Unsupported image format"
        }), 400


    try:

        # ====================================================
        # SAVE IMAGE
        # ====================================================

        original_name = secure_filename(
            image_file.filename
        )

        extension = original_name.rsplit(
            ".",
            1
        )[1].lower()

        filename = (
            str(uuid.uuid4())
            + "."
            + extension
        )

        image_path = (
            UPLOAD_FOLDER / filename
        )

        image_file.save(
            str(image_path)
        )


        # ====================================================
        # OPEN IMAGE
        # ====================================================

        image = Image.open(
            image_path
        ).convert("RGB")


        # ====================================================
        # RESIZE
        # ====================================================

        image = image.resize(
            (128, 128)
        )


        # ====================================================
        # CONVERT TO NUMPY
        # ====================================================

        image_array = np.array(
            image,
            dtype=np.float32
        )


        # ====================================================
        # ADD BATCH DIMENSION
        # ====================================================

        image_array = np.expand_dims(
            image_array,
            axis=0
        )


        # ====================================================
        # PREDICTION
        # ====================================================

        prediction_result = model.predict(
            image_array,
            verbose=0
        )


        # ====================================================
        # FIND PREDICTED CLASS
        # ====================================================

        predicted_index = int(
            np.argmax(
                prediction_result[0]
            )
        )


        # ====================================================
        # CONFIDENCE
        # ====================================================

        confidence = float(
            np.max(
                prediction_result[0]
            ) * 100
        )

        confidence = round(
            confidence,
            2
        )


        # ====================================================
        # CLASS NAME
        # ====================================================

        predicted_class = class_names[
            predicted_index
        ]


        # ====================================================
        # GET CROP + DISEASE
        # ====================================================

        crop, disease = format_disease_name(
            predicted_class
        )


        # ====================================================
        # SEVERITY
        # ====================================================

        severity = calculate_severity(
            confidence,
            disease
        )


        # ====================================================
        # FARMER ID
        # ====================================================

        farmer_id = request.form.get(
            "farmer_id"
        )


        # ====================================================
        # SAVE SCAN HISTORY
        # ====================================================

        if farmer_id:

            try:

                connection = sqlite3.connect(
                    str(DATABASE)
                )

                cursor = connection.cursor()

                cursor.execute(
                    """
                    INSERT INTO scan_history
                    (
                        farmer_id,
                        crop,
                        disease,
                        confidence,
                        severity,
                        image_path
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        farmer_id,
                        crop,
                        disease,
                        confidence,
                        severity,
                        str(image_path)
                    )
                )

                connection.commit()

                connection.close()

                print(
                    "Scan history saved successfully."
                )

            except Exception as error:

                print(
                    "Scan history error:",
                    error
                )


        # ====================================================
        # RESPONSE
        # ====================================================

        return jsonify({

            "success": True,

            "message":
                "Image analyzed successfully",

            "result": {

                "crop":
                    crop,

                "disease":
                    disease,

                "confidence":
                    confidence,

                "severity":
                    severity,

                "image":
                    filename
            }

        })


    except Exception as error:

        print(
            "Prediction error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# SCAN HISTORY API
# ============================================================

@prediction.route(
    "/history/<int:farmer_id>",
    methods=["GET"]
)
def history(farmer_id):

    try:

        connection = sqlite3.connect(
            str(DATABASE)
        )

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                crop,
                disease,
                confidence,
                severity,
                image_path,
                created_at
            FROM scan_history
            WHERE farmer_id = ?
            ORDER BY created_at DESC
            """,
            (farmer_id,)
        )

        scans = cursor.fetchall()

        connection.close()


        history_data = []

        for scan in scans:

            history_data.append({

                "id":
                    scan["id"],

                "crop":
                    scan["crop"],

                "disease":
                    scan["disease"],

                "confidence":
                    scan["confidence"],

                "severity":
                    scan["severity"],

                "image":
                    scan["image_path"],

                "date":
                    scan["created_at"]
            })


        return jsonify({

            "success": True,

            "history":
                history_data

        })


    except Exception as error:

        print(
            "History error:",
            error
        )

        return jsonify({
            

            "success": False,

            "message":
                "Unable to retrieve scan history"

        }), 500
