const payload = JSON.parse(document.getElementById('lang-data').textContent);
const state = { language: 'en', facilitiesFilter: 'all' };

function $(s) { return document.querySelector(s); }
function $all(s) { return Array.from(document.querySelectorAll(s)); }
function t(key) {
  const lang = payload.ui[state.language] || payload.ui.en;
  return lang[key] || payload.ui.en[key] || key;
}
function el(tag, cls, html) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html !== undefined) n.innerHTML = html;
  return n;
}

// Detect app language code from BCP-47 speech result tag
function detectLangFromSpeech(bcp47) {
  if (!bcp47) return null;
  const code = bcp47.toLowerCase().split('-')[0];
  return { en:'en', hi:'hi', gu:'gu', mr:'mr', ta:'ta' }[code] || null;
}

function switchScreen(screen) {
  $all('.screen').forEach(s => s.classList.remove('active'));
  $all('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('#screen-' + screen).classList.add('active');
  $all('.nav-btn[data-screen="' + screen + '"]').forEach(b => b.classList.add('active'));
  if (screen === 'nearby') loadFacilities();
  if (screen === 'asha') loadPatients();
  if (screen === 'reminders') loadMedicines();
}

function addMessage(text, sender) {
  sender = sender || 'ai';
  const wrap = el('div', 'message ' + sender);
  const bubble = el('div', 'bubble');
  bubble.textContent = text;
  wrap.appendChild(bubble);
  const msgs = document.getElementById('chat-messages');
  msgs.appendChild(wrap);
  msgs.scrollTop = msgs.scrollHeight;
}

function showTyping(show) {
  const ex = document.getElementById('typing-indicator');
  if (ex) ex.remove();
  if (!show) return;
  const wrap = el('div', 'message ai');
  wrap.id = 'typing-indicator';
  const b = el('div', 'bubble typing-bubble');
  b.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
  wrap.appendChild(b);
  const msgs = document.getElementById('chat-messages');
  msgs.appendChild(wrap);
  msgs.scrollTop = msgs.scrollHeight;
}

function addSystemGreeting() {
  document.getElementById('chat-messages').innerHTML = '';
  fetch('/api/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: '/clear_session', language: state.language })
  }).catch(() => {});
  addMessage(t('chat_greeting'), 'ai');
}

function renderQuickReplies() {
  const box = document.getElementById('quick-replies');
  box.innerHTML = '';
  (payload.quickReplies[state.language] || payload.quickReplies.en).forEach(reply => {
    const btn = el('button', 'chip', reply);
    btn.onclick = () => sendMessage(reply);
    box.appendChild(btn);
  });
}

function renderResultCard(data) {
  const old = document.getElementById('last-result-card');
  if (old) old.remove();
  if (data.is_greeting || !data.urgency) return;
  const mode = data.urgency === 'EMERGENCY' ? 'emergency' : data.urgency === 'VISIT CLINIC' ? 'clinic' : 'selfcare';
  const icons = { emergency: '🚨', clinic: '🏥', selfcare: '💊' };
  const card = el('div', 'result-card ' + mode);
  card.id = 'last-result-card';
  const likely = (data.likely_conditions || []).map(item => {
    const pct = Math.round((item.score || 0) * 100);
    const prec = item.precautions && item.precautions.length ? '<br><small style="color:#666">• ' + item.precautions.join(' • ') + '</small>' : '';
    return '<li><strong>' + item.name + '</strong> — ' + pct + '%' + prec + '</li>';
  }).join('');
  const fac = data.facility || {};
  const sympList = (data.symptoms || []).join(', ') || '—';
  card.innerHTML =
    '<div class="result-title">' +
      '<div class="result-icon">' + icons[mode] + '</div>' +
      '<div><h3>' + (data.urgency_label || '') + '</h3><p>' + (data.advice || '') + '</p></div>' +
    '</div>' +
    '<p><strong>' + t('matched_symptoms') + ':</strong> ' + sympList + '</p>' +
    '<p><strong>' + t('result_reason') + ':</strong> ' + (data.reason || '') + '</p>' +
    (data.next_question ? '<p><strong>' + t('next_question') + ':</strong> ' + data.next_question + '</p>' : '') +
    (likely ? '<div class="meta likely-list"><strong>' + t('likely_conditions') + ':</strong><ul>' + likely + '</ul></div>' : '') +
    (fac.name ? '<p><strong>' + t('recommended_facility') + ':</strong> ' + fac.name + (fac.distance_km ? ' • ' + fac.distance_km + ' km' : '') + ' • ' + (fac.type_label || fac.type || '') + '</p>' : '') +
    '<div class="actions">' +
      (mode === 'emergency' && fac.phone ? '<a class="danger-btn" href="tel:' + fac.phone + '">📞 ' + t('call') + ' 108</a>' : '') +
      (fac.map_url ? '<button class="small-btn" onclick="window.open(\'' + fac.map_url + '\', \'_blank\')">🗺️ Map</button>' : '') +
      '<button class="small-btn" id="view-nearby-btn">' + t('view_nearby') + '</button>' +
      '<button class="small-btn" id="share-wa-btn" style="background:#25D366;color:white;border:none;">Share ➔ WA</button>' +
      (data.session_id && (mode === 'emergency' || mode === 'clinic') ? '<a class="small-btn primary-btn" target="_blank" href="/referral/' + data.session_id + '/" style="background:var(--danger);color:white;border:none;">📄 Download Referral PDF</a>' : '') +
    '</div>';
  document.getElementById('chat-messages').appendChild(card);
  document.getElementById('view-nearby-btn').onclick = () => switchScreen('nearby');
  document.getElementById('share-wa-btn').onclick = () => {
      const rawSymp = data.symptoms.join(', ');
      const rawDiag = (data.likely_conditions || []).map(c => c.name).join(', ');
      const txt = `SwasthyaSaathi Triage Update\n\nUrgency: ${data.urgency_label || ''}\nSymptoms: ${rawSymp}\nDiagnoses: ${rawDiag}\n\nView nearby facilities for more detail.`;
      window.open('https://wa.me/?text=' + encodeURIComponent(txt));
  };
}

// Voice recognition language map — try native script first
// Chrome supports gu-IN, hi-IN, mr-IN, ta-IN on most systems
const VOICE_LANG = { en: 'en-IN', hi: 'hi-IN', gu: 'gu-IN', mr: 'mr-IN', ta: 'ta-IN' };
const TTS_LANG   = { en: 'en-IN', hi: 'hi-IN', gu: 'gu-IN', mr: 'mr-IN', ta: 'ta-IN' };

function speakText(text) {
  if (!window.speechSynthesis || !text) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = TTS_LANG[state.language] || 'en-IN';
  u.rate = 0.9;
  window.speechSynthesis.speak(u);
}

function initVoice() {
  const btn = document.getElementById('voice-btn');
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    btn.title = 'Voice not supported — use Chrome/Edge';
    btn.style.opacity = '0.4';
    btn.onclick = () => addMessage('🎤 Voice input requires Chrome or Edge browser.', 'ai');
    return;
  }
  let listening = false, rec = null;
  btn.onclick = () => {
    if (listening) { if (rec) rec.stop(); return; }
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    rec = new SR();
    rec.lang = VOICE_LANG[state.language] || 'en-IN';
    rec.interimResults = false;
    rec.maxAlternatives = 3;
    listening = true;
    btn.innerHTML = '🔴';
    btn.title = 'Listening… tap to stop';
    try { rec.start(); } catch(e) {
      listening = false; btn.innerHTML = '🎤'; btn.title = t('voice');
      addMessage('🎤 Could not start mic. Click 🔒 in address bar → allow microphone → refresh.', 'ai');
      return;
    }
    rec.onresult = e => {
      const transcript = e.results[0][0].transcript;
      const spokenLang = detectLangFromSpeech(rec.lang);
      if (spokenLang && spokenLang !== state.language) {
        state.language = spokenLang;
        const sel = document.getElementById('language-select');
        if (sel) sel.value = spokenLang;
        renderQuickReplies();
        addMessage('🌐 Language switched to: ' + spokenLang.toUpperCase(), 'ai');
      }
      
      document.getElementById('chat-input').value = transcript;
      listening = false; btn.innerHTML = '🎤'; btn.title = t('voice');
      sendMessage(transcript);
    };
    rec.onerror = e => {
      listening = false; btn.innerHTML = '🎤'; btn.title = t('voice');
      const map = {
        'not-allowed': '🎤 Mic blocked. Click 🔒 in address bar → Microphone → Allow → refresh.',
        'no-speech':   '🎤 No speech detected. Please try again.',
        'network':     '🎤 Network error. Voice needs internet.',
        'aborted':     ''
      };
      const msg = e.error in map ? map[e.error] : '🎤 Voice error: ' + e.error;
      if (msg) addMessage(msg, 'ai');
    };
    rec.onend = () => { listening = false; btn.innerHTML = '🎤'; btn.title = t('voice'); };
  };
}

async function requestLocation() {
  if (state.lat && state.lng) return;
  if (!navigator.geolocation) return;
  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 3500 });
    });
    state.lat = pos.coords.latitude;
    state.lng = pos.coords.longitude;
  } catch(e) {}
}

async function sendMessage(text) {
  text = (text || '').trim();
  if (!text) return;
  addMessage(text, 'user');
  document.getElementById('chat-input').value = '';
  showTyping(true);
  
  await requestLocation();

  try {
    const res = await fetch('/api/chat/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, language: state.language, lat: state.lat, lng: state.lng })
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    showTyping(false);
    
    if (data.detected_language && data.detected_language !== state.language) {
      state.language = data.detected_language;
      const sel = document.getElementById('language-select');
      if (sel) sel.value = state.language;
      renderQuickReplies();
      addMessage('🌐 Switched language to: ' + data.detected_language.toUpperCase(), 'ai');
    }

    addMessage(data.text, 'ai');
    speakText(data.text);
    renderResultCard(data);
  } catch(err) {
    showTyping(false);
    addMessage(t('bot_error'), 'ai');
    console.error('Chat error:', err);
  }
}

async function loadFacilities() {
  const list = document.getElementById('facility-list');
  list.innerHTML = '<p class="loading-text">Loading Nearby Care (Searching GPS location)...</p>';
  
  let lat = null, lng = null;
  if (navigator.geolocation) {
    try {
      const pos = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 4000 });
      });
      lat = pos.coords.latitude;
      lng = pos.coords.longitude;
    } catch (e) { console.log('Geolocation denied or timeout'); }
  }

  try {
    let url = '/api/facilities/?type=' + state.facilitiesFilter + '&language=' + state.language;
    if (lat && lng) url += '&lat=' + lat + '&lng=' + lng;
    const res = await fetch(url);
    const data = await res.json();
    list.innerHTML = '';
    if (!data.facilities.length) { list.innerHTML = '<p class="loading-text">No facilities found.</p>'; return; }
    data.facilities.forEach(f => {
      const badge = f.type === 'hospital' ? 'emergency' : f.type === 'clinic' ? 'clinic' : 'selfcare';
      const card = el('div', 'facility-card');
      card.innerHTML =
        '<div class="facility-top">' +
          '<div><h3>' + f.name + '</h3>' +
          '<div class="meta">' + f.address + '</div>' +
          '<div class="meta">' + f.distance_km + ' km • ' + f.availability + '</div></div>' +
          '<span class="badge ' + badge + '">' + (f.type_label || f.type) + '</span>' +
        '</div>' +
        '<div class="actions">' +
          '<a class="primary-btn" href="tel:' + f.phone + '">' + t('call') + '</a>' +
          '<a class="small-btn" target="_blank" href="' + (f.map_url || ('https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(f.address))) + '">' + t('directions') + '</a>' +
        '</div>';
      list.appendChild(card);
    });
  } catch(e) { list.innerHTML = '<p class="loading-text">Could not load facilities.</p>'; }
}

function renderEmergencyTiles() {
  const grid = document.getElementById('emergency-grid');
  grid.innerHTML = '';
  const colors = ['#cf3d2e','#b91c1c','#ea580c','#7c3aed','#2563eb','#4338ca'];
  (payload.emergencyItems[state.language] || payload.emergencyItems.en).forEach((item, i) => {
    const tile = el('div', 'emergency-tile');
    tile.innerHTML =
      '<div class="emergency-icon" style="background:' + colors[i % colors.length] + '">' + item.icon + '</div>' +
      '<h3>' + item.title + '</h3>' +
      '<p class="meta">' + t('tap_steps') + '</p>';
    tile.onclick = () => openEmergencyDetail(item);
    grid.appendChild(tile);
  });
}

function openEmergencyDetail(item) {
  document.getElementById('emergency-detail-content').innerHTML =
    '<div class="emergency-icon" style="background:#cf3d2e;margin-bottom:12px">' + item.icon + '</div>' +
    '<h2>' + item.title + '</h2>' +
    '<p class="meta"><strong>' + t('warning') + ':</strong> ' + item.warning + '</p>' +
    '<ol>' + item.steps.map(s => '<li style="margin-bottom:8px">' + s + '</li>').join('') + '</ol>' +
    '<a class="danger-btn full" href="tel:108">' + t('call_108') + '</a>';
  document.getElementById('emergency-detail').classList.remove('hidden');
}

async function loadPatients() {
  const list = document.getElementById('patient-list');
  list.innerHTML = '<p class="loading-text">Loading…</p>';
  try {
    const res = await fetch('/api/patients/');
    const data = await res.json();
    list.innerHTML = '';
    document.getElementById('stat-total').textContent = data.patients.length;
    document.getElementById('stat-high').textContent = data.patients.filter(p => p.priority === 'high').length;
    document.getElementById('stat-pending').textContent = data.patients.filter(p => p.priority === 'high' || p.priority === 'medium').length;
    if (!data.patients.length) { list.innerHTML = '<p class="loading-text">No patients yet.</p>'; return; }
    data.patients.forEach(p => {
      const card = el('div', 'patient-card');
      card.innerHTML =
        '<div class="patient-top">' +
          '<div><h3>' + p.name + '</h3>' +
          '<div class="meta">' + p.age + ' • ' + p.gender + '</div>' +
          '<div class="meta">' + p.village + ' • ' + p.condition + '</div></div>' +
          '<span class="tag ' + p.priority + '">' + t(p.priority) + '</span>' +
        '</div>' +
        '<div class="actions">' +
          '<a class="primary-btn" href="tel:' + p.phone + '">' + t('call') + '</a>' +
          '<button class="small-btn quick-triage-btn">' + t('quick_triage') + '</button>' +
        '</div>';
      card.querySelector('.quick-triage-btn').onclick = () => {
        switchScreen('chat');
        sendMessage(p.name + ', ' + p.age + ', ' + p.condition);
      };
      list.appendChild(card);
    });
  } catch(e) { list.innerHTML = '<p class="loading-text">Could not load patients.</p>'; }
}

async function addPatient() {
  const name = document.getElementById('patient-name').value.trim();
  if (!name) { alert('Please enter patient name.'); return; }
  try {
    await fetch('/api/patients/add/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name,
        age: document.getElementById('patient-age').value,
        gender: document.getElementById('patient-gender').value,
        village: document.getElementById('patient-village').value,
        phone: document.getElementById('patient-phone').value,
        condition: document.getElementById('patient-condition').value,
        priority: document.getElementById('patient-priority').value
      })
    });
    ['patient-name','patient-age','patient-gender','patient-village','patient-phone','patient-condition'].forEach(id => { document.getElementById(id).value = ''; });
    loadPatients();
  } catch(e) { alert('Could not add patient.'); }
}

async function loadMedicines() {
  const list = document.getElementById('medicine-list');
  list.innerHTML = '<p class="loading-text">Loading…</p>';
  try {
    const res = await fetch('/api/profile/medicines/');
    const data = await res.json();
    list.innerHTML = '';
    
    if (!data.medicines || !data.medicines.length) { 
        list.innerHTML = '<p class="loading-text" style="grid-column: 1/-1; text-align: center; margin-top: 2rem;">No medicines added yet.</p>'; 
        return; 
    }
    
    data.medicines.forEach(m => {
      const card = el('div', 'medicine-card');
      card.innerHTML =
        '<div class="medicine-top">' +
          '<div><h3>' + m.name + '</h3>' +
          '<div class="meta" style="margin-top:0.25rem;">' + m.time + (m.quantity ? ' • <span style="font-weight:600; color:var(--primary);">' + m.quantity + '</span>' : '') + '</div></div>' +
          '<span class="tag ' + (m.taken ? 'low' : 'medium') + '">' + (m.taken ? t('taken') : t('pending_label')) + '</span>' +
        '</div>' +
        '<div class="actions" style="display: flex; gap: 0.5rem; justify-content: space-between;">' +
          '<button class="primary-btn toggle-btn" data-mid="' + m.id + '" style="flex: 1;">' + (m.taken ? t('mark_untaken') : t('mark_taken')) + '</button>' +
          '<button class="primary-btn edit-btn" data-mid="' + m.id + '" style="background: none; border: 1px solid var(--primary); color: var(--primary); padding: 0.5rem; opacity: 0.8;"><span style="font-size:1.1rem">✏️</span></button>' +
          '<button class="primary-btn del-btn" data-mid="' + m.id + '" style="background: none; border: 1px solid #ef4444; color: #ef4444; padding: 0.5rem; opacity: 0.8;"><span style="font-size:1.1rem">🗑</span></button>' +
        '</div>';
        
      card.querySelector('.toggle-btn').onclick = async () => {
        await fetch('/api/profile/medicines/', { 
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({id: m.id})
        });
        loadMedicines();
      };
      
      card.querySelector('.del-btn').onclick = async () => {
        if(confirm("Delete this medicine?")) {
            await fetch('/api/profile/medicines/', { 
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({id: m.id})
            });
            loadMedicines();
        }
      };
      
      card.querySelector('.edit-btn').onclick = () => {
          document.getElementById('edit-med-id').value = m.id;
          document.getElementById('new-med-name').value = m.name;
          document.getElementById('new-med-qty').value = m.quantity || '';
          document.getElementById('new-med-time').value = m.time || '';
          document.getElementById('add-medicine-modal').style.display = 'flex';
      };
      
      list.appendChild(card);
    });
  } catch(e) { list.innerHTML = '<p class="loading-text">Could not load medicines.</p>'; }
}

async function submitCustomMedicine() {
    const btn = document.querySelector('#add-medicine-modal button[type="submit"]');
    const oldText = btn.textContent;
    btn.textContent = "Saving...";
    btn.disabled = true;
    
    try {
        await fetch('/api/profile/medicines/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: document.getElementById('edit-med-id').value,
                name: document.getElementById('new-med-name').value,
                quantity: document.getElementById('new-med-qty').value,
                time: document.getElementById('new-med-time').value
            })
        });
        
        document.getElementById('new-med-name').value = '';
        document.getElementById('new-med-qty').value = '';
        document.getElementById('new-med-time').value = '';
        
        document.getElementById('add-medicine-modal').style.display = 'none';
        loadMedicines();
    } catch (e) {
        alert("Failed to add medicine.");
    } finally {
        btn.textContent = oldText;
        btn.disabled = false;
    }
}

async function triggerSOS(phoneNumber) {
    const btn = document.getElementById('sos-btn');
    const statusBox = document.getElementById('sos-status');
    
    if (btn) {
        btn.innerHTML = 'Sending...';
        btn.style.opacity = '0.8';
        btn.disabled = true;
    }
    if (statusBox) statusBox.textContent = "Fetching GPS coordinates...";
    
    let payload = {};
    try {
        const pos = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {timeout: 5000});
        });
        payload = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        if (statusBox) statusBox.textContent = "Location acquired. Dispatching emergency email...";
    } catch(e) {
        if (statusBox) statusBox.textContent = "GPS failing. Sending network ping only...";
    }
    
    let hasEmailError = false;
    try {
        const response = await fetch('/api/emergency/sos/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Backend alert email failed.");
        }
        if (statusBox) statusBox.textContent = "Family has been successfully emailed!";
    } catch(e) {
        hasEmailError = true;
        if (statusBox) {
            statusBox.style.color = "#ef4444";
            statusBox.textContent = "Email Error: " + e.message;
        }
    }
    
    // Give user time to read the specific SMTP error before taking over their screen with dialer
    setTimeout(() => {
        if (statusBox) {
            statusBox.style.color = "var(--text)";
            statusBox.textContent = "Launching Phone Dialer...";
        }
        window.location.href = "tel:" + phoneNumber;
        
        if (btn) {
            btn.innerHTML = '<span style="font-size: 1.5rem;">🔴</span> TRIGGER SOS';
            btn.style.opacity = '1';
            btn.disabled = false;
        }
    }, hasEmailError ? 4500 : 1500);
}

function applyLanguage() {
  document.documentElement.lang = state.language;
  const map = {
    'app-title':'app_title','tagline':'tagline','topbar-title':'app_title','topbar-subtitle':'tagline',
    'desktop-hint':'desktop_hint','send-btn':'send','quick-title':'quick_title',
    'nearby-title':'nearby_title','nearby-subtitle':'nearby_subtitle',
    'filter-all':'all','filter-hospital':'hospital','filter-clinic':'clinic','filter-pharmacy':'pharmacy',
    'emergency-header':'emergency_header','emergency-sub':'emergency_sub','call-108-btn':'call_108',
    'asha-title':'asha_title','asha-subtitle':'asha_subtitle',
    'stat-total-label':'patients','stat-high-label':'high_priority','stat-today-label':'today','stat-pending-label':'pending',
    'add-patient-title':'add_patient','add-patient-btn':'add_patient_btn',
    'medicine-title':'medicine_title','medicine-subtitle':'medicine_subtitle','daily-badge':'daily',
    'profile-title':'app_title','profile-subtitle':'profile_subtitle',
    'emergency-numbers-title':'emergency_numbers','about-title':'about','about-text':'about_text',
    'disclaimer-title':'disclaimer','disclaimer-text':'disclaimer_text'
  };
  Object.keys(map).forEach(id => { const n = document.getElementById(id); if (n) n.textContent = t(map[id]); });
  document.getElementById('chat-input').placeholder = t('placeholder');
  document.getElementById('patient-name').placeholder = t('full_name');
  document.getElementById('patient-age').placeholder = t('age');
  document.getElementById('patient-gender').placeholder = t('gender');
  document.getElementById('patient-village').placeholder = t('village');
  document.getElementById('patient-phone').placeholder = t('phone');
  document.getElementById('patient-condition').placeholder = t('condition');
  const pri = document.getElementById('patient-priority');
  if (pri) { pri.options[0].text = t('low'); pri.options[1].text = t('medium'); pri.options[2].text = t('high'); }
  $all('[data-label]').forEach(e => { e.textContent = t(e.dataset.label); });
  addSystemGreeting();
  renderQuickReplies();
  renderEmergencyTiles();
}

function init() {
  $all('.nav-btn').forEach(btn => {
    if (btn.dataset.screen) {
      btn.onclick = () => switchScreen(btn.dataset.screen);
    }
  });
  $all('[data-filter-type]').forEach(btn => btn.onclick = () => {
    $all('[data-filter-type]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.facilitiesFilter = btn.dataset.filterType;
    loadFacilities();
  });
  
  const sendBtn = document.getElementById('send-btn');
  const chatInput = document.getElementById('chat-input');
  if (sendBtn && chatInput) {
    sendBtn.onclick = () => sendMessage(chatInput.value);
    chatInput.addEventListener('keydown', e => { 
      if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage(chatInput.value);
      }
    });
  }

  const langSelect = document.getElementById('language-select');
  if (langSelect) {
    langSelect.onchange = e => { state.language = e.target.value; applyLanguage(); };
  }

  const addPatientBtn = document.getElementById('add-patient-btn');
  if (addPatientBtn) addPatientBtn.onclick = addPatient;
  
  const closeEm = document.getElementById('close-emergency-detail');
  if (closeEm) closeEm.onclick = () => document.getElementById('emergency-detail').classList.add('hidden');
  
  const emBackdrop = document.querySelector('#emergency-detail .modal-backdrop');
  if (emBackdrop) emBackdrop.onclick = () => document.getElementById('emergency-detail').classList.add('hidden');

  if (typeof initVoice === 'function') initVoice();
  if (typeof applyLanguage === 'function') applyLanguage();
  if (typeof loadFacilities === 'function') loadFacilities();
  if (typeof loadPatients === 'function') loadPatients();
  if (typeof loadMedicines === 'function') loadMedicines();
}

document.addEventListener('DOMContentLoaded', init);
