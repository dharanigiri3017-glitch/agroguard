// ==========================================================
// AGROGUARD AI - RESULT.JS
// ==========================================================

console.log("Result page loaded");


// Get saved prediction
const savedResult =
    localStorage.getItem("predictionResult");


console.log(
    "Saved prediction:",
    savedResult
);


const resultContainer =
    document.getElementById(
        "resultContainer"
    );


// ==========================================================
// CHECK RESULT
// ==========================================================

if (!savedResult) {

    resultContainer.innerHTML = `
        <div class="item">
            ❌ No prediction result found.
        </div>
    `;

} else {

    try {

        const result =
            JSON.parse(savedResult);


        console.log(
            "Parsed result:",
            result
        );


        resultContainer.innerHTML = `

            <div class="item">
                <span class="label">
                    🌱 Crop:
                </span>
                ${result.crop || "Unknown"}
            </div>


            <div class="item">
                <span class="label">
                    🦠 Disease:
                </span>
                ${result.disease || "Unknown"}
            </div>


            <div class="item">
                <span class="label">
                    📊 Confidence:
                </span>
                ${result.confidence || 0}%
            </div>


            <div class="item">
                <span class="label">
                    ⚠️ Severity:
                </span>
                ${result.severity || "Unknown"}
            </div>

        `;

    }

    catch (error) {

        console.error(
            "Result parsing error:",
            error
        );

        resultContainer.innerHTML = `
            <div class="item">
                ❌ Unable to display prediction result.
            </div>
        `;

    }

}


// ==========================================================
// SCAN AGAIN
// ==========================================================

function goScanner() {

    window.location.href =
        "scanner.html";

}
