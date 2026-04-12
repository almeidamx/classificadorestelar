const API_URL = "http://localhost:5000/predict";

/* ---- Star field ---- */
(function initStarfield() {
  const canvas = document.getElementById("starfield");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const STAR_COUNT   = 320;
  const BRIGHT_COUNT = 28;
  const stars = [];

  function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function rand(min, max) {
    return Math.random() * (max - min) + min;
  }

  const PALETTE = [
    "255,255,255",
    "255,255,255",
    "255,255,255",
    "220,240,255",
    "180,220,255",
    "0,212,255",
    "255,229,102",
    "200,180,255",
  ];

  function buildStars() {
    stars.length = 0;
    for (let i = 0; i < STAR_COUNT; i++) {
      stars.push({
        x:      rand(0, canvas.width),
        y:      rand(0, canvas.height),
        r:      rand(0.3, 1.1),
        color:  PALETTE[Math.floor(rand(0, 3))],
        alpha:  rand(0.4, 1.0),
        speed:  rand(0.0003, 0.0012),
        offset: rand(0, Math.PI * 2),
        glow:   false,
      });
    }
    for (let i = 0; i < BRIGHT_COUNT; i++) {
      stars.push({
        x:      rand(0, canvas.width),
        y:      rand(0, canvas.height),
        r:      rand(1.2, 2.2),
        color:  PALETTE[Math.floor(rand(0, PALETTE.length))],
        alpha:  rand(0.7, 1.0),
        speed:  rand(0.0004, 0.001),
        offset: rand(0, Math.PI * 2),
        glow:   true,
      });
    }
  }

  function draw(timestamp) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const s of stars) {
      const a = s.alpha * (0.6 + 0.4 * Math.sin(timestamp * s.speed + s.offset));
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      if (s.glow) {
        ctx.shadowBlur  = 8;
        ctx.shadowColor = `rgba(${s.color},${a})`;
      } else {
        ctx.shadowBlur = 0;
      }
      ctx.fillStyle = `rgba(${s.color},${a})`;
      ctx.fill();
    }
    ctx.shadowBlur = 0;
    requestAnimationFrame(draw);
  }

  resize();
  buildStars();
  requestAnimationFrame(draw);

  window.addEventListener("resize", () => {
    resize();
    buildStars();
  });
})();
/* ---- End star field ---- */

function getFormData() {
  const rawFields = {
    alpha:    document.getElementById("alpha").value,
    delta:    document.getElementById("delta").value,
    u:        document.getElementById("u").value,
    g:        document.getElementById("g").value,
    r:        document.getElementById("r").value,
    i:        document.getElementById("i").value,
    z:        document.getElementById("z").value,
    redshift: document.getElementById("redshift").value,
  };

  for (const [, value] of Object.entries(rawFields)) {
    if (value === "" || value === null) {
      return null;
    }
  }

  const fields = {
    alpha:    parseFloat(rawFields.alpha),
    delta:    parseFloat(rawFields.delta),
    u:        parseFloat(rawFields.u),
    g:        parseFloat(rawFields.g),
    r:        parseFloat(rawFields.r),
    i:        parseFloat(rawFields.i),
    z:        parseFloat(rawFields.z),
    redshift: parseFloat(rawFields.redshift),
  };

  const validations = [
    { field: "alpha",    min: 0.0,   max: 360.0, label: "Ascensão Reta (α)" },
    { field: "delta",    min: -90.0, max: 90.0,  label: "Declinação (δ)" },
    { field: "u",        min: -10.0, max: 35.0,  label: "Banda U" },
    { field: "g",        min: -10.0, max: 35.0,  label: "Banda G" },
    { field: "r",        min: -10.0, max: 35.0,  label: "Banda R" },
    { field: "i",        min: -10.0, max: 35.0,  label: "Banda I" },
    { field: "z",        min: -10.0, max: 35.0,  label: "Banda Z" },
    { field: "redshift", min: -0.05, max: 10.0,  label: "Redshift" },
  ];

  for (const v of validations) {
    const value = fields[v.field];
    if (isNaN(value) || value < v.min || value > v.max) {
      return { error: `${v.label} deve estar entre ${v.min} e ${v.max}` };
    }
  }

  return fields;
}

async function classify() {
  const errorMsg   = document.getElementById("errorMsg");
  const loading    = document.getElementById("loading");
  const resultPanel = document.getElementById("resultPanel");
  const btn        = document.getElementById("classifyBtn");

  errorMsg.classList.remove("show");
  resultPanel.classList.remove("show");

  const data = getFormData();

  if (!data) {
    errorMsg.textContent = "⚠ PREENCHA TODOS OS CAMPOS PARA CONTINUAR ⚠";
    errorMsg.classList.add("show");
    return;
  }

  if (data.error) {
    errorMsg.textContent = `⚠ ${data.error} ⚠`;
    errorMsg.classList.add("show");
    return;
  }

  loading.classList.add("show");
  btn.disabled = true;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      const backendError = payload?.error || "Erro na API";
      errorMsg.textContent = `⚠ ${backendError} ⚠`;
      errorMsg.classList.add("show");
      return;
    }

    showResult(payload.prediction);
  } catch {
    errorMsg.textContent = "⚠ ERRO DE CONEXÃO COM O SERVIDOR ⚠";
    errorMsg.classList.add("show");
  } finally {
    loading.classList.remove("show");
    btn.disabled = false;
  }
}

function showResult(prediction) {
  const resultPanel = document.getElementById("resultPanel");
  const resultValue = document.getElementById("resultValue");
  const resultIcon  = document.getElementById("resultIcon");
  const resultDesc  = document.getElementById("resultDesc");

  const info = {
    STAR: {
      label: "ESTRELA",
      icon:  "⭐",
      desc:  "Objeto estelar próximo — redshift praticamente nulo, pertence à Via Láctea.",
      cls:   "star",
    },
    GALAXY: {
      label: "GALÁXIA",
      icon:  "🌌",
      desc:  "Sistema de bilhões de estrelas — redshift positivo moderado (0,0–1,0).",
      cls:   "galaxy",
    },
    QSO: {
      label: "QUASAR",
      icon:  "✨",
      desc:  "Núcleo galáctico ultraenergético — redshift elevado, altíssima luminosidade.",
      cls:   "qso",
    },
  };

  const obj = info[prediction] || {
    label: prediction,
    icon:  "❓",
    desc:  "",
    cls:   "",
  };

  resultIcon.textContent  = obj.icon;
  resultValue.textContent = obj.label;
  resultValue.className   = "result-value " + obj.cls;
  resultDesc.textContent  = obj.desc;

  resultPanel.classList.add("show");
  resultPanel.scrollIntoView({ behavior: "smooth" });
}

function resetForm() {
  document.querySelectorAll("input").forEach((input) => (input.value = ""));
  document.getElementById("resultPanel").classList.remove("show");
  document.getElementById("errorMsg").classList.remove("show");
  window.scrollTo({ top: 0, behavior: "smooth" });
}
