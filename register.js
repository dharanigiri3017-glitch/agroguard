document.getElementById("registerForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const message = document.getElementById("message");

    const farmerData = {

        name: document.getElementById("name").value,

        mobile: document.getElementById("mobile").value,

        email: document.getElementById("email").value,

        password: document.getElementById("password").value,

        crop: document.getElementById("crop").value

    };

    message.innerText = "Registering...";

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/auth/register",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(farmerData)
            }
        );

        const data = await response.json();

        if (response.ok && data.success) {

            message.innerText =
                "✅ " + data.message;

            document.getElementById("registerForm").reset();

        } else {

            message.innerText =
                "❌ " + data.message;

        }

    } catch (error) {

        console.error("Registration error:", error);

        message.innerText =
            "❌ Cannot connect to AgroGuard AI server.";

    }

});
