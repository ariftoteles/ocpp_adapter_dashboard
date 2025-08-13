let DB = null;

// ---------- helpers ----------
const $  = (sel)=>document.querySelector(sel);
const $$ = (sel)=>Array.from(document.querySelectorAll(sel));
const setText = (id, v)=>{const el=document.getElementById(id); if(el) el.textContent = v ?? "";};

// ---------- API ----------
async function fetchDB() {
  const token = localStorage.getItem("token");
  if (!token) {
    location.href = "login.html";
    return;
  }

  try {
    const r = await fetch("http://localhost:8000/api/data", {
      cache: "no-store",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (r.status === 401) { // Token invalid
      localStorage.removeItem("token");
      location.href = "login.html";
      return;
    }

    if (!r.ok) throw new Error(`HTTP error! status: ${r.status}`);

    DB = await r.json();
    console.log("Database loaded:", DB);
  } catch (err) {
    console.error("Gagal fetch DB:", err);
  }
}

async function saveDB() {
  const token = localStorage.getItem("token");
  if (!token) {
    location.href = "login.html";
    return;
  }

  try {
    const r = await fetch("http://localhost:8000/api/save", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(DB)
    });

    if (r.status === 401) {
      localStorage.removeItem("token");
      location.href = "login.html";
      return;
    }

    if (!r.ok) throw new Error(`HTTP error! status: ${r.status}`);

    const resData = await r.json();
    console.log("Database saved:", resData);
  } catch (err) {
    console.error("Gagal simpan DB:", err);
    alert("Gagal menyimpan data ke server");
  }
}

// ---------- render information ----------
function renderInformation(){
  const g=DB.general, f=DB.uplink_forward_to, u=DB.uplink_to;
  console.log(g, "<<< g");
  
  setText("info-name", g.name);
  setText("info-ip", g.ip_address);
  setText("info-port", g.port);
  setText("info-protocol-fwd", f.protocol_forward_to);
  setText("info-url-fwd", f.url_forward_to);
  setText("info-port-fwd", f.port_forward_to);
  setText("info-protocol-up", u.protocol_uplink_to);
  setText("info-ip-up", u.ip_address_uplink_to);
  setText("info-port-up", u.port_uplink_to);
  setText("info-id-up", u.id_modbus_uplink_to);
}

// ---------- render general ----------
function renderGeneral(){
  const g=DB.general;
  $("#gen-name").value = g.name||"";
  $("#gen-ip").value   = g.ip_address||"";
  $("#gen-port").value = g.port||"";
  $("#save-general").onclick = async ()=>{
    DB.general.name = $("#gen-name").value.trim();
    DB.general.ip_address = $("#gen-ip").value.trim();
    DB.general.port = $("#gen-port").value.trim();
    await saveDB();
    renderInformation();
    alert("General saved");
  };
}

// ---------- render uplink ----------
function renderUplink(){
  const f=DB.uplink_forward_to, u=DB.uplink_to;
  $("#fwd-protocol").value = f.protocol_forward_to||"";
  $("#fwd-url").value      = f.url_forward_to||"";
  $("#fwd-port").value     = f.port_forward_to||"";
  $("#up-protocol").value  = u.protocol_uplink_to||"";
  $("#up-ip").value        = u.ip_address_uplink_to||"";
  $("#up-port").value      = u.port_uplink_to||"";
  $("#up-id").value        = u.id_modbus_uplink_to||"";
  $("#save-uplink").onclick = async ()=>{
    DB.uplink_forward_to.url_forward_to = $("#fwd-url").value.trim();
    DB.uplink_forward_to.port_forward_to = $("#fwd-port").value.trim();
    DB.uplink_to.ip_address_uplink_to = $("#up-ip").value.trim();
    DB.uplink_to.port_uplink_to = $("#up-port").value.trim();
    DB.uplink_to.id_modbus_uplink_to = $("#up-id").value.trim();
    await saveDB();
    renderInformation();
    alert("Uplink saved");
  };
}

// ---------- render data point ----------
function renderDataPoint(){
  const tbody = $("#dp-tbody");
  tbody.innerHTML = "";
  DB.data_point.slice().sort((a,b)=>a.address-b.address||a.id-b.id).forEach((row,i)=>{
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${i+1}</td>
      <td>${row.ocpp_name}</td>
      <td>${row.function_code}</td>
      <td>${row.address}</td>
      <td>${row.data_type}</td>
      <td><input type="checkbox" data-id="${row.id}" ${row.is_active?"checked":""}></td>`;
    tbody.appendChild(tr);
  });

  $("#save-table").classList.remove("hidden");
  tbody.onchange = (e)=>{
    const cb = e.target;
    if(cb && cb.matches('input[type="checkbox"][data-id]')){
      const id = +cb.dataset.id;
      const item = DB.data_point.find(x=>x.id===id);
      if(item) item.is_active = cb.checked;
    }
  };
  $("#save-table").onclick = async ()=>{ await saveDB(); alert("Data Point saved"); };
}

document.getElementById("btn-logout").addEventListener("click", () => {
  localStorage.removeItem("token");
  location.href = "login.html";
});

// ---------- routing ----------
const routes = {
  "information": ()=>{ $("#save-table").classList.add("hidden"); renderInformation(); },
  "general":     ()=>{ $("#save-table").classList.add("hidden"); renderGeneral(); },
  "uplink":      ()=>{ $("#save-table").classList.add("hidden"); renderUplink(); },
  "data-point":  ()=>{ renderDataPoint(); }
};

function showPage(name) {
  // sembunyikan semua halaman
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));

  // tampilkan halaman sesuai hash
  const targetPage = document.getElementById(`page-${name}`);
  if (targetPage) targetPage.classList.add("active");

  // set judul halaman
  document.getElementById("page-title").textContent = ({
    "information": "Information",
    "general": "Configuration General",
    "uplink": "Configuration Uplink",
    "data-point": "Configuration Data Point"
  })[name] || "Information";

  // buka submenu kalau di halaman konfigurasi
  const submenu = document.querySelector(".submenu");
  submenu.style.display = ["general", "uplink", "data-point"].includes(name) ? "block" : "none";

  // 🟢 tambahkan ini untuk memanggil render halaman
  if (routes[name]) {
    routes[name]();
  }
}

function bindSidebar() {
  // tombol group
  const btn = document.querySelector(".group-btn");
  const submenu = document.querySelector(".submenu");
  btn.onclick = () => {
    submenu.style.display = submenu.style.display === "block" ? "none" : "block";
  };

  // semua link sidebar
  document.querySelectorAll(".sidebar a").forEach(link => {
    link.addEventListener("click", e => {
      const hash = link.getAttribute("href");
      const name = hash.replace("#", "");
      showPage(name);
    });
  });
}

// ---------- init ----------
(async function init() {
  const token = localStorage.getItem("token");
  if (!token) {
    location.href = "login.html";
    return;
  }

  await fetchDB();
  if (!DB) return; // Kalau gagal fetch, jangan lanjut

  bindSidebar();

  const startPage = (location.hash || "#information").slice(1);
  showPage(startPage);

  window.addEventListener("hashchange", () => {
    const page = (location.hash || "#information").slice(1);
    showPage(page);
  });
})();

