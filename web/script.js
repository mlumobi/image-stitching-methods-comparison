let startTime = null;
let timerInterval = null;
let currentOutputs = null;

// Append messages to the readonly status "command window" and auto-scroll.
function appendStatus(msg, clear = false) {
  const el = document.getElementById('status');
  if (!el) return;
  if (clear) {
    el.value = '';
  }
  // Normalize message and append newline
  const text = String(msg);
  if (el.value && !el.value.endsWith('\n')) el.value += '\n';
  el.value += text;
  // Auto-scroll to bottom
  el.scrollTop = el.scrollHeight;
}

// File name display
document.getElementById('img1').addEventListener('change', function() {
  document.getElementById('name1').textContent = this.files.length ? this.files[0].name : 'No file';
});

document.getElementById('img2').addEventListener('change', function() {
  document.getElementById('name2').textContent = this.files.length ? this.files[0].name : 'No file';
});

// Start timer
function startTimer() {
  startTime = Date.now();
  const timingDiv = document.getElementById('timing');
  timingDiv.style.display = 'block';
  
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
  const saveBtn = document.getElementById('saveBtn');
  
  try {
    appendStatus('Uploading images...', true);
    runBtn.disabled = true;
    saveBtn.style.display = 'none';
    startTimer();

    const buffer1 = await img1.arrayBuffer();
    const buffer2 = await img2.arrayBuffer();
    
  appendStatus('Processing: Converting images...');
    const path1 = await window.pywebview.api.save_temp_file(Array.from(new Uint8Array(buffer1)), img1.name);
    const path2 = await window.pywebview.api.save_temp_file(Array.from(new Uint8Array(buffer2)), img2.name);
    
  appendStatus(`Running ${method} stitching... This may take a few seconds.`);
    const outputs = await window.pywebview.api.run_pipeline(path1, path2, method);

  stopTimer();
    
    // Store results for save function
    currentOutputs = {
      method: method,
      timestamp: new Date().toISOString(),
      outputs: outputs
    };

  appendStatus('Stitching complete!');
    
    // Load images into tabs
    if (outputs.stitched) document.getElementById('output_stitched').src = outputs.stitched;
    if (outputs.matches) document.getElementById('output_matches').src = outputs.matches;
    if (outputs.features1) document.getElementById('output_feat1').src = outputs.features1;
    if (outputs.features2) document.getElementById('output_feat2').src = outputs.features2;
    
    // Show save button
    saveBtn.style.display = 'block';
    
  // All panes are visible on the same page; no tab switching required.
  } catch (error) {
    stopTimer();
    appendStatus(`✗ Error: ${error.message}`);
    console.error(error);
  } finally {
    runBtn.disabled = false;
  }
}

// Save results
async function saveResults() {
  if (!currentOutputs) {
    alert("No results to save!");
    return;
  }

  const { method, outputs } = currentOutputs;
  
  // Download each image
  if (outputs.stitched) {
    downloadImage(outputs.stitched, `stitched_${method.toLowerCase()}.jpg`);
  }
  if (outputs.matches) {
    downloadImage(outputs.matches, `matches_${method.toLowerCase()}.jpg`);
  }
  if (outputs.features1) {
    downloadImage(outputs.features1, `features1_${method.toLowerCase()}.jpg`);
  }
  if (outputs.features2) {
    downloadImage(outputs.features2, `features2_${method.toLowerCase()}.jpg`);
  }

  alert("Results saved! Check your Downloads folder.");
}

// Helper to download image from data URI
function downloadImage(dataUri, filename) {
  const link = document.createElement('a');
  link.href = dataUri;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Initialize Panzoom for stitched image with proper zoom in/out
(function () {
  const img = document.getElementById('output_stitched');
  if (!img) return;

  function initializePanzoom() {
    const container = img.parentElement;

    container.style.display = 'flex';
    container.style.justifyContent = 'center';
    container.style.alignItems = 'center';
    container.style.overflow = 'hidden';

    const panzoom = Panzoom(img, {
      minScale: 0.2,   // allow zoom out
      maxScale: 10,    // allow zoom in
      cursor: 'grab',
      contain: false
     });

    container.addEventListener('wheel', panzoom.zoomWithWheel);
  }

  if (img.complete && img.naturalWidth !== 0) {
    initializePanzoom();
  } else {
    img.addEventListener('load', initializePanzoom);
  }
})();

// Initialize Panzoom for matches image with proper zoom in/out
(function () {
  const img = document.getElementById('output_matches');
  if (!img) return;

  function initializePanzoom() {
    const container = img.parentElement;

    container.style.display = 'flex';
    container.style.justifyContent = 'center';
    container.style.alignItems = 'center';
    container.style.overflow = 'hidden';

    const panzoom = Panzoom(img, {
      minScale: 0.2,   // allow zoom out
      maxScale: 10,    // allow zoom in
      cursor: 'grab',
      contain: false
     });

    container.addEventListener('wheel', panzoom.zoomWithWheel);
  }

  if (img.complete && img.naturalWidth !== 0) {
    initializePanzoom();
  } else {
    img.addEventListener('load', initializePanzoom);
  }
})();

// Initialize Panzoom for features1 image with proper zoom in/out
(function () {
  const img = document.getElementById('output_feat1');
  if (!img) return;

  function initializePanzoom() {
    const container = img.parentElement;

    container.style.display = 'flex';
    container.style.justifyContent = 'center';
    container.style.alignItems = 'center';
    container.style.overflow = 'hidden';

    const panzoom = Panzoom(img, {
      minScale: 0.2,   // allow zoom out
      maxScale: 10,    // allow zoom in
      cursor: 'grab',
      contain: false
     });

    container.addEventListener('wheel', panzoom.zoomWithWheel);
  }

  if (img.complete && img.naturalWidth !== 0) {
    initializePanzoom();
  } else {
    img.addEventListener('load', initializePanzoom);
  }
})();

// Initialize Panzoom for features2 image with proper zoom in/out
(function () {
  const img = document.getElementById('output_feat2');
  if (!img) return;

  function initializePanzoom() {
    const container = img.parentElement;

    container.style.display = 'flex';
    container.style.justifyContent = 'center';
    container.style.alignItems = 'center';
    container.style.overflow = 'hidden';

    const panzoom = Panzoom(img, {
      minScale: 0.2,   // allow zoom out
      maxScale: 10,    // allow zoom in
      cursor: 'grab',
      contain: false
     });

    container.addEventListener('wheel', panzoom.zoomWithWheel);
  }

  if (img.complete && img.naturalWidth !== 0) {
    initializePanzoom();
  } else {
    img.addEventListener('load', initializePanzoom);
  }
})();