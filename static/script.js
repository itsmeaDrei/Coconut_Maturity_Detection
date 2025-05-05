function previewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById("previewImage").src = e.target.result;
            document.getElementById("previewImage").classList.remove("hidden");
        };
        reader.readAsDataURL(file);
    }
}

function analyzeImage() {
    const fileInput = document.getElementById("fileInput");
    if (!fileInput.files.length) return alert("Please select an image first!");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    document.getElementById("resultsText").innerText = "Analyzing...";

    fetch("/analyze", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("resultsText").innerText = data.error;
            return;
        }

        // Prevent browser caching
        const timestamp = new Date().getTime();
        document.getElementById("processedImage").src = data.image_url + "?t=" + timestamp;
        document.getElementById("processedImage").classList.remove("hidden");

        // Display results
        let resultText = "<h3>Detection Counts:</h3>";
        resultText += `<p>Stage 1: ${data.results.stage1}</p>`;
        resultText += `<p>Stage 2: ${data.results.stage2}</p>`;
        resultText += `<p>Stage 3: ${data.results.stage3}</p>`;
        resultText += `<p>Total Coconuts: ${data.results.total}</p>`;
        document.getElementById("resultsText").innerHTML = resultText || "No coconuts detected.";
    })
    .catch(error => {
        document.getElementById("resultsText").innerText = "Error processing image.";
        console.error("Error:", error);
    });
}   