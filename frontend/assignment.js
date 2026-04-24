const API = "http://127.0.0.1:5000";

function createAssignment() {
    fetch(API + "/assignment", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            title: document.getElementById("title").value,
            description: document.getElementById("desc").value,
            due_date: document.getElementById("due").value,
            teacher_id: localStorage.getItem("user_id")
        })
    }).then(() => loadAssignments());
}

function loadAssignments() {
    fetch(API + "/assignment")
    .then(res => res.json())
    .then(data => {
        let html = "";
        data.forEach(a => {
            html += `
            <div>
                <h3>${a[1]}</h3>
                <p>${a[2]}</p>
                <p>Due: ${a[3]}</p>
                <button onclick="deleteAssignment(${a[0]})">Delete</button>
            </div>`;
        });
        document.getElementById("assignments").innerHTML = html;
    });
}

function deleteAssignment(id) {
    fetch(API + "/assignment/" + id, {
        method: "DELETE"
    }).then(() => loadAssignments());
}