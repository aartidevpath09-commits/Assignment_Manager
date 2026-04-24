const API = "http://127.0.0.1:5000";

function register() {
    fetch(API + "/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            name: document.getElementById("name").value,
            email: document.getElementById("email").value,
            password: document.getElementById("password").value,
            role: document.getElementById("role").value
        })
    })
    .then(res => res.json())
    .then(data => {
        alert("Registered successfully");
        window.location = "login.html";
    });
}

function login() {
    fetch(API + "/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            email: document.getElementById("email").value,
            password: document.getElementById("password").value
        })
    })
    .then(res => res.json())
    .then(data => {
        localStorage.setItem("token", data.token);
        localStorage.setItem("role", data.role);
        localStorage.setItem("user_id", data.id);

        if (data.role === "teacher") {
            window.location = "teacher.html";
        } else {
            window.location = "dashboard.html";
        }
    });
}