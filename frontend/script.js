const API = "http://127.0.0.1:5000";

function getAuthHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + localStorage.getItem("token")
    };
}
// =====================
// REGISTER
// =====================
function register() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const role = document.getElementById("role").value;

    if (!username || !password) {
        alert("All fields required");
        return;
    }

    fetch(`${API}/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password, role})
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        window.location.href = "login.html";
    })
    .catch(() => alert("Register failed"));
}

// =====================
// LOGIN (with backend)
// =====================
function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;
    
    showLoader();

    fetch(`${API}/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password, role})
    })
    .then(res => res.json())
    .then(data => {
        if (data.message === "Login Success") {
            
            localStorage.setItem("token", data.token);
            localStorage.setItem("user_id", data.user_id);
            localStorage.setItem("role", data.role);
            localStorage.removeItem("notified");

            if (role === "student") {
                window.location.href = "dashboard_student.html";
            } else {
                window.location.href = "dashboard_teacher.html";
            }
        } else {
            alert("Invalid credentials");
        }
    })
    .catch(() => {
    hideLoader(); // ✅ error case
    alert("Login error");
});
}

// =====================
// LOGOUT
// =====================
function logout() {
    if (confirm("Are you sure you want to logout?")) {
        localStorage.removeItem("user_id");
        localStorage.removeItem("role");
        localStorage.removeItem("notified");
        window.location.href = "login.html";
    }
}


function loadNotifications() {
    const user_id = localStorage.getItem("user_id");

    fetch(`${API}/notifications/${user_id}`)
    .then(res => res.json())
    .then(data => {
        const list = document.getElementById("notificationList");
        list.innerHTML = "";

        data.forEach(n => {
            list.innerHTML += `
            <div class="assignment-card">
                <p>${n.message}</p>
                <small>${n.time}</small>
            </div>`;
        });
    });
}
// =====================
// PROTECT DASHBOARD
// =====================
function checkAuth() {
    const user_id = localStorage.getItem("user_id");
    const role = localStorage.getItem("role");

    if (!user_id || !role) {
        alert("Please login first");
        window.location.href = "login.html";
    }
}

// =====================
// TEACHER CRUD
// =====================

// CREATE
function addAssignment() {
    const title = document.getElementById("title").value;
    const subject = document.getElementById("subject").value;
    const dueDate = document.getElementById("dueDate").value;

    if (!title || !subject || !dueDate) {
        alert("Fill all fields");
        return;
    }

    showLoader(); 

    fetch(`${API}/assignments`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
            title,
            subject,
            due_date: dueDate
        })
    })
    .then(res => res.json())
    .then(data => {
        hideLoader();

        alert(data.message || "Assignment Added");
        loadAssignments();

        // clear form
        document.getElementById("title").value = "";
        document.getElementById("subject").value = "";
        document.getElementById("dueDate").value = "";
    })
    .catch(() => {
        hideLoader();
        alert("Error adding assignment");
    });
}

// READ
function loadAssignments() {
    showLoader(); 
    fetch(`${API}/assignments`)
    .then(res => res.json())
    .then(data => {
        hideLoader();
        const list = document.getElementById("assignmentList");
        if (!list) return;

        list.innerHTML = "";

        data.forEach(a => {
            list.innerHTML += `
            <div class="assignment-card">
                <h3>${a.title}</h3>
                <p>${a.subject}</p>
                <p><b>Due:</b> ${a.due_date}</p>
                <button onclick="deleteAssignment(${a.id})">Delete</button>
            </div>`;
        });

        loadStats(data);
        loadChart(data);
    });
    
}

// DELETE
function deleteAssignment(id) {
    if (!confirm("Delete this assignment?")) return;

    fetch(`${API}/assignments/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
        }
    })
    .then(() => loadAssignments())
    .catch(() => alert("Delete failed"));
}

// =====================
// STUDENT
// =====================

// VIEW
function loadStudentAssignments() {
    fetch(`${API}/assignments`)
    .then(res => res.json())
    .then(data => {
    const list = document.getElementById("assignmentList");
    list.innerHTML = "";

    data.forEach(a => {
       list.innerHTML += `
<div class="assignment-card">
    <h3>${a.title}</h3>
    <p>Due: ${a.due_date}</p>

    <input type="file" id="file-${a.id}">
    <button onclick="uploadPDF(${a.id}, event)">Upload</button>
</div>`;
    });

    // 🔔 check notifications
    checkDueDates(data);
    loadStudentStats(data);
    loadStudentChart(data);

    });
}


function checkDueDates(assignments) {
    const today = new Date().toISOString().split("T")[0];

    assignments.forEach(a => {
        if (a.due_date === today) {
            showNotification("⚠️ Due Today!", a.title);
        }
    });
}


// =====================
// FILE UPLOAD (PDF)
// =====================
function uploadPDF(assignment_id, event) {

    const btn = event.target;

    btn.disabled = true;
    btn.innerText = "Uploading...";

    const fileInput = document.getElementById(`file-${assignment_id}`);
    const file = fileInput.files[0];

    let formData = new FormData();
    formData.append("file", file);
    formData.append("assignment_id", assignment_id);
    formData.append("student_id", localStorage.getItem("user_id"));

    fetch(`${API}/upload`, {
        method: "POST",
        headers: {
        "Authorization": "Bearer " + localStorage.getItem("token")
    },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);

        btn.disabled = false;
        btn.innerText = "Upload";
    })
    .catch(() => {
        btn.disabled = false;
        btn.innerText = "Upload";
        alert("Upload failed");
    });
}


// =====================
// SUBMISSIONS (Teacher)
// =====================
function loadSubmissions() {
    fetch(`${API}/submissions`)
    .then(res => res.json())
    .then(data => {
        const list = document.getElementById("submissionList");
        if (!list) return;

        list.innerHTML = "";

        data.forEach(s => {
            list.innerHTML += `
            <div class="assignment-card">
                <h4>${s.title}</h4>
                <a href="${API}/uploads/${s.file}" target="_blank">
                    View / Download
                </a>
            </div>`;
        });
    });
}

function showNotification(title, message) {
    if ("Notification" in window) {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                new Notification(title, {
                    body: message
                });
            }
        });
    }
}


function loadStats(assignments) {
    const total = assignments.length;

    const today = new Date().toISOString().split("T")[0];

    let dueToday = 0;

    assignments.forEach(a => {
        if (a.due_date === today) {
            dueToday++;
        }
    });

    document.getElementById("totalCount").innerText = total;
    document.getElementById("dueToday").innerText = dueToday;
}


function loadChart(assignments) {
    const ctx = document.getElementById("myChart");

    const labels = assignments.map(a => a.title);
    const data = assignments.map(() => 1);

    // 🔥 OLD chart delete (IMPORTANT)
    if (window.myChartInstance) {
        window.myChartInstance.destroy();
    }

    // ✅ create new chart
    window.myChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Assignments',
                data: data
            }]
        }
    });
}

function loadStudentStats(assignments) {
    const total = assignments.length;

    const today = new Date().toISOString().split("T")[0];

    let dueToday = 0;
    let upcoming = 0;

    assignments.forEach(a => {
        if (a.due_date === today) {
            dueToday++;
        } else if (a.due_date > today) {
            upcoming++;
        }
    });

    document.getElementById("stuTotal").innerText = total;
    document.getElementById("stuDueToday").innerText = dueToday;
    document.getElementById("stuUpcoming").innerText = upcoming;
}

function loadStudentChart(assignments) {
    const ctx = document.getElementById("studentChart");

    let dueToday = 0;
    let upcoming = 0;
    let past = 0;

    const today = new Date().toISOString().split("T")[0];

    assignments.forEach(a => {
        if (a.due_date === today) dueToday++;
        else if (a.due_date > today) upcoming++;
        else past++;
    });

    // 🔥 IMPORTANT FIX (duplicate chart remove)
    if (window.studentChartInstance) {
        window.studentChartInstance.destroy();
    }

    // 🔥 new chart create
    window.studentChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Due Today', 'Upcoming', 'Past'],
            datasets: [{
                data: [dueToday, upcoming, past]
            }]
        }
    });
}

function showLoader() {
    document.body.style.opacity = "0.5";
}

function hideLoader() {
    document.body.style.opacity = "1";
}
// =====================
// AUTO LOAD
// =====================
window.onload = function() {
    const title = document.title;

    // 🔐 Protect dashboard pages
    if (title.includes("Dashboard")) {
        checkAuth();
    }

    if (title.includes("Teacher")) {
        loadAssignments();
        loadSubmissions();
    }

    if (title.includes("Student")) {
        loadStudentAssignments();

        // 🔔 LOAD NOTIFICATIONS (ADD THIS)
        loadNotifications();
    }

    // 🔔 Welcome Notification (only once)
    if (!localStorage.getItem("notified")) {
        showNotification("Welcome 🎉", "Dashboard loaded successfully!");
        localStorage.setItem("notified", "true");
    }
};