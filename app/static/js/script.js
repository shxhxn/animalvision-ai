/* ==========================================================================
   app/static/js/script.js

   No frameworks -- plain DOM APIs and fetch(). Split into small named
   functions (initThemeToggle, initUploadForm, ...) each responsible for one
   page feature, called once on DOMContentLoaded. Every init function checks
   its elements exist before wiring up listeners, so this single file can
   safely be included on every page even though not every page has every
   element.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();
    initUploadForm();
    initClearHistory();
    initRetrainButton();
});

/* ---------------------------------------------------------------------- */
/* Dark mode                                                               */
/* ---------------------------------------------------------------------- */
function initThemeToggle() {
    const toggleBtn = document.getElementById("theme-toggle");
    const icon = document.getElementById("theme-icon");
    if (!toggleBtn) return;

    const applyTheme = (theme) => {
        document.documentElement.setAttribute("data-theme", theme);
        icon.textContent = theme === "dark" ? "☀️" : "🌙";
    };

    const savedTheme = localStorage.getItem("animalvision-theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    applyTheme(savedTheme);

    toggleBtn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";
        applyTheme(next);
        localStorage.setItem("animalvision-theme", next);
    });
}

/* ---------------------------------------------------------------------- */
/* Upload form (Predict page)                                             */
/* ---------------------------------------------------------------------- */
function initUploadForm() {
    const form = document.getElementById("upload-form");
    if (!form) return;

    const fileInput = document.getElementById("file-input");
    const dropZone = document.getElementById("drop-zone");
    const dropZoneEmpty = document.getElementById("drop-zone-empty");
    const previewImage = document.getElementById("preview-image");
    const predictBtn = document.getElementById("predict-btn");
    const loadingIndicator = document.getElementById("loading-indicator");
    const errorBox = document.getElementById("error-box");
    const resultSection = document.getElementById("result-section");

    let chartInstance = null;

    const showPreview = (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.style.display = "block";
            dropZoneEmpty.style.display = "none";
        };
        reader.readAsDataURL(file);
        predictBtn.disabled = false;
    };

    fileInput.addEventListener("change", () => {
        if (fileInput.files[0]) showPreview(fileInput.files[0]);
    });

    // Drag and drop support
    ["dragover", "dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (e) => e.preventDefault());
    });
    dropZone.addEventListener("dragover", () => dropZone.classList.add("drag-over"));
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
    dropZone.addEventListener("drop", (e) => {
        dropZone.classList.remove("drag-over");
        const file = e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files;
            showPreview(file);
        }
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!fileInput.files[0]) return;

        errorBox.style.display = "none";
        resultSection.style.display = "none";
        loadingIndicator.style.display = "block";
        predictBtn.disabled = true;

        const formData = new FormData();
        formData.append("image", fileInput.files[0]);

        try {
            const response = await fetch("/predict", { method: "POST", body: formData });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Prediction failed.");
            }

            renderResult(data);
        } catch (err) {
            errorBox.textContent = err.message;
            errorBox.style.display = "block";
        } finally {
            loadingIndicator.style.display = "none";
            predictBtn.disabled = false;
        }
    });

    function renderResult(data) {
        document.getElementById("result-label").textContent = data.predicted_class;
        document.getElementById("result-confidence").textContent = data.confidence;
        resultSection.style.display = "block";

        const ctx = document.getElementById("prediction-chart").getContext("2d");
        const labels = data.top_predictions.map((p) => p.label);
        const values = data.top_predictions.map((p) => p.confidence);

        if (chartInstance) chartInstance.destroy();

        const accentColor = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim();

        chartInstance = new Chart(ctx, {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: "Confidence (%)",
                    data: values,
                    backgroundColor: accentColor,
                    borderRadius: 6,
                }],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true, max: 100 } },
            },
        });

        resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
}

/* ---------------------------------------------------------------------- */
/* Clear history (History page)                                          */
/* ---------------------------------------------------------------------- */
function initClearHistory() {
    const btn = document.getElementById("clear-history-btn");
    if (!btn) return;

    btn.addEventListener("click", async () => {
        if (!confirm("Clear all prediction history? This can't be undone.")) return;
        await fetch("/history/clear", { method: "POST" });
        window.location.reload();
    });
}

/* ---------------------------------------------------------------------- */
/* Retrain button (Model Performance page)                               */
/* ---------------------------------------------------------------------- */
function initRetrainButton() {
    const btn = document.getElementById("retrain-btn");
    const statusBox = document.getElementById("retrain-status");
    if (!btn) return;

    btn.addEventListener("click", async () => {
        if (!confirm("Retrain the model using the current contents of data/raw/? This can take several minutes.")) return;

        btn.disabled = true;
        statusBox.style.display = "block";
        statusBox.className = "alert alert-info";
        statusBox.textContent = "Training in progress... this page will stay open until it finishes.";

        try {
            const response = await fetch("/retrain", { method: "POST" });
            const data = await response.json();

            if (!response.ok) throw new Error(data.error || "Retraining failed.");

            statusBox.className = "alert alert-info";
            statusBox.textContent = data.status + " Reloading results...";
            setTimeout(() => window.location.reload(), 1500);
        } catch (err) {
            statusBox.className = "alert alert-error";
            statusBox.textContent = err.message;
            btn.disabled = false;
        }
    });
}