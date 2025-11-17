let startTime = null;
let timerInterval = null;
let currentOutputs = null;

// Transparent 1x1 PNG to avoid Chrome broken image icons
const EMPTY_IMAGE =
  "data:image/png;base64," +
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQV" +
  "R42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";

// Append status to console-like box
function appendStatus(msg, clear = false) {
  const el = document.getElementById('status');
  if (!el) return;
  if (clear) el.value = '';
  if (el.value && !el.value.endsWith('\n')) {
    el.value += '\n';
  }
  el.value += msg;
  el.scrollTop = el.scrollHeight;
}

// Display selected filenames
document.getElementById('img1').addEventListener('change', function() {
  document.getElementById('name1').textContent =
    this.files.length ? this.files[0].name : 'No file';
});
document.getElementById('img2').addEventListener('change', function() {
  document.getElementById('name2').textContent =
    this.files.length ? this.files[0].name : 'No file';
});

// Start timer
function startTimer() {
  startTime = Date.now();
  document.getElementById('timing').style.display = 'block';

  timerInterval = setInterval(() => {
    const elapsedMs = Date.now() - startTime;
    const seconds = Math.floor(elapsedMs / 1000);
    const milliseconds = elapsedMs % 1000;
    const formatted = `${seconds}.${String(milliseconds).padStart(3, '0')}`;
    document.getElementById('elapsed').textContent = formatted;
  }, 10);
}

// Stop timer
function stopTimer() {
  if (timerInterval) clearInterval(timerInterval);
}

// Set image with safe default
function setImage(id, src) {
  const img = document.getElementById(id);
  img.src = src || EMPTY_IMAGE;
}

// Run stitching
async function run(event) {
  const img1 = document.getElementById('img1').files[0];
  const img2 = document.getElementById('img2').files[0];
  const method = document.getElementById('method').value;

  if (!img1 || !img2) {
    alert("Please select both images!");
    return;
  }

  const runBtn = document.getElementById('runBtn');

  try {
    appendStatus("Uploading images...", true);
    runBtn.disabled = true;
    startTimer();

    const formData = new FormData();
    formData.append("img1", img1);
    formData.append("img2", img2);
    formData.append("method", method);

    appendStatus(`Running ${method} stitching...`);

    const response = await fetch("/api/run_pipeline", {
      method: "POST",
      body: formData
    });

    const outputs = await response.json();
    stopTimer();

    appendStatus("Stitching complete!");
    currentOutputs = outputs;

    // Load images with safe default
    setImage("output_feat1", outputs.features1);
    setImage("output_feat2", outputs.features2);
    setImage("output_matches", outputs.matches);
    setImage("output_stitched", outputs.stitched);

  } catch (error) {
    stopTimer();
    appendStatus(`✗ Error: ${error.message}`);
    console.error(error);
  } finally {
    runBtn.disabled = false;
  }
}

// Initialize images on page load
window.addEventListener("load", () => {
  setImage("output_feat1", EMPTY_IMAGE);
  setImage("output_feat2", EMPTY_IMAGE);
  setImage("output_matches", EMPTY_IMAGE);
  setImage("output_stitched", EMPTY_IMAGE);
});