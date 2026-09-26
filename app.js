function startProject() {

    document.getElementById("status").innerText =
        "⏳ Connecting to AgroGuard AI server...";

    fetch("http://127.0.0.1:5000/api/health")

        .then(response => {

            if (!response.ok) {
                throw new Error("Backend server error");
            }

            return response.json();
        })

        .then(data => {

            document.getElementById("status").innerText =
                "✅ Backend Connected! " + data.system;

            console.log("Backend response:", data);
        })

        .catch(error => {

            document.getElementById("status").innerText =
                "❌ Backend connection failed.";

            console.error("Connection error:", error);
        });
}
