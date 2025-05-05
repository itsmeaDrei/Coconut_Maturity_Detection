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

        // Update the processed image
        const processedImage = document.getElementById("processedImage");
        const timestamp = new Date().getTime();
        processedImage.src = data.image_url + "?t=" + timestamp;
        processedImage.classList.remove("hidden");

        // Set results text (with confidence level)
        const resultsContainer = document.getElementById("resultsText");
        resultsContainer.innerHTML = `
            <div>
                <h3>Detection Results</h3>
                <p><strong>Stage 1:</strong> ${data.results.stage1}</p>
                <p><strong>Stage 2:</strong> ${data.results.stage2}</p>
                <p><strong>Stage 3:</strong> ${data.results.stage3}</p>
                <p><strong>Total Coconuts:</strong> ${data.results.total}</p>
                <p><strong>Average Confidence Level:</strong> ${data.results.confidence}%</p>
            </div>
        `;
    })
    .catch(error => {
        document.getElementById("resultsText").innerText = "Error processing image.";
        console.error("Error:", error);
    });
}
const header = document.querySelector('.header');

window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    header.classList.add('visible');
  } else {
    header.classList.remove('visible');
  }
});