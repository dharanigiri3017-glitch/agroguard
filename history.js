const historyContainer =
    document.getElementById(
        "historyContainer"
    );


// --------------------------------------------------
// CHECK LOGIN
// --------------------------------------------------

const farmerData =
    localStorage.getItem("farmer");


if (!farmerData) {

    alert(
        "Please login first."
    );

    window.location.href =
        "login.html";

}


// --------------------------------------------------
// GET FARMER
// --------------------------------------------------

const farmer =
    JSON.parse(farmerData);


// --------------------------------------------------
// LOAD HISTORY
// --------------------------------------------------

async function loadHistory() {

    historyContainer.innerHTML =
        "<p>Loading scan history...</p>";


    try {

        const response =
            await fetch(
                "http://127.0.0.1:5000/api/prediction/history/"
                + farmer.id
            );


        const data =
            await response.json();


        console.log(
            "History response:",
            data
        );


        if (
            response.ok &&
            data.success
        ) {

            displayHistory(
                data.history
            );

        } else {

            historyContainer.innerHTML =
                "<p>Unable to load scan history.</p>";

        }


    } catch (error) {

        console.error(
            "History error:",
            error
        );


        historyContainer.innerHTML =
            "<p>Cannot connect to AgroGuard AI server.</p>";

    }

}


// --------------------------------------------------
// DISPLAY HISTORY
// --------------------------------------------------

function displayHistory(history) {

    if (
        !history ||
        history.length === 0
    ) {

        historyContainer.innerHTML = `

            <div>

                <h3>No Scan History</h3>

                <p>
                    You have not scanned any crops yet.
                </p>

            </div>

        `;

        return;
    }


    let html = "";


    history.forEach(function(scan) {

        html += `

            <div style="
                background: #f5f5f5;
                padding: 20px;
                margin: 15px 0;
                border-radius: 15px;
                text-align: left;
            ">

                <h3>
                    🌿 ${scan.disease}
                </h3>

                <p>
                    <b>Crop:</b>
                    ${scan.crop}
                </p>

                <p>
                    <b>Confidence:</b>
                    ${scan.confidence}%
                </p>

                <p>
                    <b>Severity:</b>
                    ${scan.severity}
                </p>

                <p>
                    <b>Date:</b>
                    ${scan.date}
                </p>

            </div>

        `;

    });


    historyContainer.innerHTML =
        html;
}


// --------------------------------------------------
// NAVIGATION
// --------------------------------------------------

function openScanner() {

    window.location.href =
        "scanner.html";

}


function goDashboard() {

    window.location.href =
        "dashboard.html";

}


// --------------------------------------------------
// START
// --------------------------------------------------

loadHistory();
