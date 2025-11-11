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
  
  try {
    appendStatus('Uploading images...', true);
    runBtn.disabled = true;
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
    
    // Load images into panes
    if (outputs.stitched) document.getElementById('output_stitched').src = outputs.stitched;
    if (outputs.matches) document.getElementById('output_matches').src = outputs.matches;
    if (outputs.features1) document.getElementById('output_feat1').src = outputs.features1;
    if (outputs.features2) document.getElementById('output_feat2').src = outputs.features2;
    

  } catch (error) {
    stopTimer();
    appendStatus(`✗ Error: ${error.message}`);
    console.error(error);
  } finally {
    runBtn.disabled = false;
  }
}

// Function to initialize Panzoom for any image element
function initPanzoom(imgId) {
  const img = document.getElementById(imgId);
  if (!img) return;

  function initialize() {
    const container = img.parentElement;
    container.style.display = 'flex';
    container.style.justifyContent = 'center';
    container.style.alignItems = 'center';
    container.style.overflow = 'hidden';

    // Attach Panzoom to the image element, not the container
    const panzoom = Panzoom(img, {
      minScale: 0.2,
      maxScale: 10,
      cursor: 'grab',
      contain: 'outside'
    });

    // Use the image itself for wheel events
    img.addEventListener('wheel', (e) => panzoom.zoomWithWheel(e, { focal: true }));
  }

  if (img.complete && img.naturalWidth !== 0) {
    initialize();
  } else {
    img.addEventListener('load', initialize);
  }
}

// Initialize Panzoom for all result images
initPanzoom('output_stitched');
initPanzoom('output_matches');
initPanzoom('output_feat1');
initPanzoom('output_feat2');