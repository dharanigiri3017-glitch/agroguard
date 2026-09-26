// ==========================================================
// AGROGUARD AI - SCANNER.JS
// ==========================================================


// ==========================================================
// GET HTML ELEMENTS
// ==========================================================

const imageInput = document.getElementById("cropImage");
const imagePreview = document.getElementById("imagePreview");
const scanMessage = document.getElementById("scanMessage");
const scanForm = document.getElementById("scanForm");


// ==========================================================
// IMAGE PREVIEW
// ==========================================================

if (imageInput) {

    imageInput.addEventListener("change", function () {

        const file = this.files[0];

        if (!file) {
            return;
        }

        // Check image type
        if (!file.type.startsWith("image/")) {

            scanMessage.innerText =
                "Please select a valid image.";

            imagePreview.style.display = "none";

            return;
        }


        // Create preview
        const imageURL =
            URL.createObjectURL(file);

        imagePreview.src = imageURL;

        imagePreview.style.display =
            "block";


        scanMessage.innerText =
            "Image selected successfully.";

    });

}


// ==========================================================
// SCAN FORM
// ==========================================================

if (scanForm) {

    scanForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            // ------------------------------------------------
            // CHECK IMAGE
            // ------------------------------------------------

            const file =
                imageInput.files[0];


            if (!file) {

                scanMessage.innerText =
                    "Please select a crop image.";

                return;
            }


            // ------------------------------------------------
            // CHECK LOGIN
            // ------------------------------------------------

            const farmerData =
                localStorage.getItem("farmer");


            if (!farmerData) {

                alert("Please login first.");

                window.location.href =
                    "login.html";

                return;
            }


            let farmer;

            try {

                farmer =
                    JSON.parse(farmerData);

            } catch (error) {

                console.error(
                    "Farmer data error:",
                    error
                );

                alert("Please login again.");

                localStorage.removeItem(
                    "farmer"
                );

                window.location.href =
                    "login.html";

                return;
            }


            // ------------------------------------------------
            // SHOW LOADING MESSAGE
            // ------------------------------------------------

            scanMessage.innerText =
                "🌱 Analyzing crop image...";


            // ------------------------------------------------
            // CREATE FORM DATA
            // ------------------------------------------------

            const formData =
                new FormData();


            formData.append(
                "image",
                file
            );


            // Add farmer ID if available
            if (farmer && farmer.id) {

                formData.append(
                    "farmer_id",
                    farmer.id
                );

            }


            // ------------------------------------------------
            // SEND IMAGE TO FLASK
            // ------------------------------------------------

            try {

                console.log(
                    "Sending image to AgroGuard AI..."
                );


                const response =
                    await fetch(
                        "http://127.0.0.1:5000/api/prediction/predict",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                console.log(
                    "Response status:",
                    response.status
                );


                // ------------------------------------------------
                // READ SERVER RESPONSE
                // ------------------------------------------------

                const responseText =
                    await response.text();


                console.log(
                    "Raw server response:",
                    responseText
                );


                let data;


                try {

                    data =
                        JSON.parse(
                            responseText
                        );

                } catch (error) {

                    console.error(
                        "JSON parsing error:",
                        error
                    );

                    scanMessage.innerText =
                        "Invalid response from AgroGuard server.";

                    return;
                }


                console.log(
                    "Prediction response:",
                    data
                );


                // ------------------------------------------------
                // SUCCESS
                // ------------------------------------------------

                if (
                    response.ok &&
                    data.success === true &&
                    data.result
                ) {

                    console.log(
                        "AI prediction successful!"
                    );


                    console.log(
                        "Crop:",
                        data.result.crop
                    );

                    console.log(
                        "Disease:",
                        data.result.disease
                    );

                    console.log(
                        "Confidence:",
                        data.result.confidence
                    );

                    console.log(
                        "Severity:",
                        data.result.severity
                    );


                    // --------------------------------------------
                    // SAVE COMPLETE RESULT
                    // --------------------------------------------

                    localStorage.setItem(
                        "predictionResult",
                        JSON.stringify(
                            data.result
                        )
                    );


                    // --------------------------------------------
                    // ALSO SAVE INDIVIDUAL VALUES
                    // --------------------------------------------

                    localStorage.setItem(
                        "predictionCrop",
                        data.result.crop || ""
                    );

                    localStorage.setItem(
                        "predictionDisease",
                        data.result.disease || ""
                    );

                    localStorage.setItem(
                        "predictionConfidence",
                        data.result.confidence || ""
                    );

                    localStorage.setItem(
                        "predictionSeverity",
                        data.result.severity || ""
                    );

                    localStorage.setItem(
                        "predictionImage",
                        data.result.image || ""
                    );


                    // --------------------------------------------
                    // SUCCESS MESSAGE
                    // --------------------------------------------

                    scanMessage.innerText =
                        "✅ Analysis completed successfully!";


                    // --------------------------------------------
                    // OPEN RESULT PAGE
                    // --------------------------------------------

                    setTimeout(function () {

                        window.location.href =
                            "result.html";

                    }, 500);

                }


                // ------------------------------------------------
                // API ERROR
                // ------------------------------------------------

                else {

                    console.error(
                        "Prediction failed:",
                        data
                    );


                    scanMessage.innerText =
                        "Prediction failed: " +
                        (
                            data.message ||
                            "Unknown API error"
                        );

                }

            }


            // ------------------------------------------------
            // CONNECTION ERROR
            // ------------------------------------------------

            catch (error) {

                console.error(
                    "AgroGuard connection error:",
                    error
                );


                scanMessage.innerText =
                    "❌ Cannot connect to AgroGuard AI server.";

            }

        }
    );

}


// ==========================================================
// DASHBOARD BUTTON
// ==========================================================

function goDashboard() {

    window.location.href =
        "dashboard.html";

}
