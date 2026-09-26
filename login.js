document.getElementById("loginForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const message = document.getElementById("message");

    const loginData = {

        email: document.getElementById("email").value,

        password: document.getElementById("password").value

    };

    message.innerText = "Logging in...";

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/auth/login",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(loginData)
            }
        );

        const data = await response.json();

        if (response.ok && data.success) {

            // Save farmer information
            localStorage.setItem(
                "farmer",
                JSON.stringify(data.farmer)
            );

            message.innerText =
                "✅ Login successful!";

            // Open dashboard
            setTimeout(function() {

                window.location.href = "dashboard.html";

            }, 700);

        } else {

            message.innerText =
                "❌ " + data.message;

        }

    } catch (error) {

        console.error("Login error:", error);

        message.innerText =
            "❌ Cannot connect to AgroGuard AI server.";

    }

});
