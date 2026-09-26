from flask import Blueprint, request, jsonify
import sqlite3
from pathlib import Path
import hashlib


# ==========================================================
# BLUEPRINT
# ==========================================================

auth = Blueprint("auth", __name__)


# ==========================================================
# DATABASE PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE = BASE_DIR / "data" / "database" / "agroguard.db"


# ==========================================================
# PASSWORD HASHING
# ==========================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():

    DATABASE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        str(DATABASE)
    )

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================================
# CREATE FARMERS TABLE
# ==========================================================

def create_table():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            mobile TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            crop TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    connection.close()


# Create table when server starts
create_table()


# ==========================================================
# REGISTER
# ==========================================================

@auth.route(
    "/register",
    methods=["POST"]
)
def register():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No registration data received"
            }), 400


        # --------------------------------------------------
        # GET DATA
        # --------------------------------------------------

        name = data.get("name", "").strip()

        mobile = data.get("mobile", "").strip()

        email = data.get("email", "").strip().lower()

        password = data.get("password", "").strip()

        crop = data.get("crop", "").strip()


        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if not name:

            return jsonify({
                "success": False,
                "message": "Name is required"
            }), 400


        if not mobile:

            return jsonify({
                "success": False,
                "message": "Mobile number is required"
            }), 400


        if not email:

            return jsonify({
                "success": False,
                "message": "Email is required"
            }), 400


        if not password:

            return jsonify({
                "success": False,
                "message": "Password is required"
            }), 400


        if len(password) < 4:

            return jsonify({
                "success": False,
                "message": "Password must contain at least 4 characters"
            }), 400


        # --------------------------------------------------
        # HASH PASSWORD
        # --------------------------------------------------

        hashed_password = hash_password(
            password
        )


        # --------------------------------------------------
        # INSERT FARMER
        # --------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO farmers
            (
                name,
                mobile,
                email,
                password,
                crop
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            mobile,
            email,
            hashed_password,
            crop
        ))


        farmer_id = cursor.lastrowid

        connection.commit()

        connection.close()


        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return jsonify({

            "success": True,

            "message":
                "Farmer registered successfully",

            "farmer": {

                "id": farmer_id,

                "name": name,

                "mobile": mobile,

                "email": email,

                "crop": crop
            }

        }), 201


    except sqlite3.IntegrityError:

        return jsonify({

            "success": False,

            "message":
                "Email already registered"

        }), 409


    except Exception as error:

        print(
            "Registration error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Registration failed"

        }), 500


# ==========================================================
# LOGIN
# ==========================================================

@auth.route(
    "/login",
    methods=["POST"]
)
def login():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No login data received"

            }), 400


        # --------------------------------------------------
        # GET LOGIN DATA
        # --------------------------------------------------

        email = data.get(
            "email",
            ""
        ).strip().lower()


        password = data.get(
            "password",
            ""
        ).strip()


        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if not email:

            return jsonify({

                "success": False,

                "message":
                    "Email is required"

            }), 400


        if not password:

            return jsonify({

                "success": False,

                "message":
                    "Password is required"

            }), 400


        # --------------------------------------------------
        # FIND FARMER
        # --------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                mobile,
                email,
                password,
                crop
            FROM farmers
            WHERE email = ?
        """, (
            email,
        ))


        farmer = cursor.fetchone()

        connection.close()


        # --------------------------------------------------
        # CHECK FARMER
        # --------------------------------------------------

        if not farmer:

            return jsonify({

                "success": False,

                "message":
                    "Invalid email or password"

            }), 401


        # --------------------------------------------------
        # CHECK PASSWORD
        # --------------------------------------------------

        hashed_password = hash_password(
            password
        )


        if hashed_password != farmer["password"]:

            return jsonify({

                "success": False,

                "message":
                    "Invalid email or password"

            }), 401


        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        return jsonify({

            "success": True,

            "message":
                "Login successful",

            "farmer": {

                "id":
                    farmer["id"],

                "name":
                    farmer["name"],

                "mobile":
                    farmer["mobile"],

                "email":
                    farmer["email"],

                "crop":
                    farmer["crop"]
            }

        })


    except Exception as error:

        print(
            "Login error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Login failed"

        }), 500


# ==========================================================
# GET FARMER PROFILE
# ==========================================================

@auth.route(
    "/farmer/<int:farmer_id>",
    methods=["GET"]
)
def get_farmer(farmer_id):

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                mobile,
                email,
                crop,
                created_at
            FROM farmers
            WHERE id = ?
        """, (
            farmer_id,
        ))


        farmer = cursor.fetchone()

        connection.close()


        if not farmer:

            return jsonify({

                "success": False,

                "message":
                    "Farmer not found"

            }), 404


        return jsonify({

            "success": True,

            "farmer": {

                "id":
                    farmer["id"],

                "name":
                    farmer["name"],

                "mobile":
                    farmer["mobile"],

                "email":
                    farmer["email"],

                "crop":
                    farmer["crop"],

                "created_at":
                    farmer["created_at"]
            }

        })


    except Exception as error:

        print(
            "Profile error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to retrieve farmer profile"

        }), 500
