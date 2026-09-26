const farmerData = localStorage.getItem("farmer");


if (!farmerData) {

    alert("Please login first!");

    window.location.href = "login.html";

} else {

    const farmer = JSON.parse(farmerData);

    document.getElementById("welcome").innerText =
        "Welcome back, " + farmer.name + "! 🌱";

    document.getElementById("farmerName").innerText =
        farmer.name;

    document.getElementById("farmerEmail").innerText =
        farmer.email;

    document.getElementById("farmerMobile").innerText =
        farmer.mobile;

    document.getElementById("farmerCrop").innerText =
        farmer.crop || "Not specified";
}


function openScanner() {

    alert("Crop Scanner will be added in the next step.");

}


function viewHistory() {
    window.location.href = "history.html";
}


function logout() {

    localStorage.removeItem("farmer");

    window.location.href = "login.html";

}
