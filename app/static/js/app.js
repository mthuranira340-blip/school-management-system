const roleSelect = document.getElementById("roleSelect");
const linkedStudentWrap = document.getElementById("linkedStudentWrap");
const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebarToggle");

function toggleLinkedStudent() {
    if (!roleSelect || !linkedStudentWrap) {
        return;
    }
    linkedStudentWrap.style.display = roleSelect.value === "parent" ? "block" : "none";
}

if (roleSelect) {
    toggleLinkedStudent();
    roleSelect.addEventListener("change", toggleLinkedStudent);
}

if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });
}

function buildChart(canvasId, label, data, type = "line") {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !data || !data.labels || !data.labels.length) {
        return;
    }

    const baseConfig = {
        type,
        data: {
            labels: data.labels,
            datasets: [
                {
                    label,
                    data: data.values,
                    borderColor: "#1f4c73",
                    backgroundColor: type === "bar" ? ["#1f4c73", "#3ca89b", "#f0b44c", "#ef7e79", "#8fb3cc"] : "rgba(60, 168, 155, 0.2)",
                    borderWidth: 3,
                    tension: 0.3,
                    fill: type !== "bar"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    };

    new Chart(canvas, baseConfig);
}

buildChart("trendChart", "Average Score", window.trendChartData, "line");
buildChart("subjectChart", "Subject Average", window.subjectChartData, "bar");
