const API = "http://127.0.0.1:5000";

// Token helper
function getToken() {
    return localStorage.getItem("token");
}

// Logout
function logout() {
    localStorage.clear();
    window.location = "login.html";
}

// Role check
function isTeacher() {
    return localStorage.getItem("role") === "teacher";
}

// Auth check
function checkAuth() {
    if (!getToken()) {
        alert("Please login first");
        window.location = "login.html";
    }
}