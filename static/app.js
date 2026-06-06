"use strict";

const state = { token: null, user: null };

const $ = (sel) => document.querySelector(sel);

async function api(path, options = {}) {
  const headers = options.headers || {};
  if (state.token) headers["Authorization"] = `Bearer ${state.token}`;
  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }
  return res.status === 204 ? null : res.json();
}

// --- Authentification ---
async function login(email, password) {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Email ou mot de passe incorrect");
  const data = await res.json();
  state.token = data.access_token;
  state.user = await api("/api/auth/me");
  localStorage.setItem("token", state.token);
}

function logout() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("token");
  render();
}

// --- Étudiants ---
async function loadStudents() {
  const tbody = $("#students-table tbody");
  tbody.innerHTML = "";
  const students = await api("/api/students");
  for (const s of students) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${s.student_number}</td>
      <td>${s.first_name} ${s.last_name}</td>
      <td>${s.program || "-"}</td>
      <td>${s.email}</td>
      <td>
        <a class="link" href="/api/students/${s.id}/transcript.csv" target="_blank">CSV</a>
        <a class="link" href="/api/students/${s.id}/transcript.pdf" target="_blank">PDF</a>
      </td>
      <td><button class="btn btn-danger btn-small" data-del="${s.id}">Supprimer</button></td>`;
    tbody.appendChild(tr);
  }
  tbody.querySelectorAll("[data-del]").forEach((btn) =>
    btn.addEventListener("click", async () => {
      await api(`/api/students/${btn.dataset.del}`, { method: "DELETE" });
      loadStudents();
    })
  );
}

async function createStudent(payload) {
  await api("/api/students", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

// --- Rendu ---
function render() {
  const logged = Boolean(state.token);
  $("#login-view").classList.toggle("hidden", logged);
  $("#dashboard").classList.toggle("hidden", !logged);
  $("#session-info").classList.toggle("hidden", !logged);
  if (logged && state.user) {
    $("#user-label").textContent = `${state.user.full_name} (${state.user.role})`;
    const isAdmin = state.user.role === "admin";
    $("#student-form-card").classList.toggle("hidden", !isAdmin);
    loadStudents();
  }
}

// --- Initialisation ---
document.addEventListener("DOMContentLoaded", () => {
  $("#login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    $("#login-error").textContent = "";
    try {
      await login($("#login-email").value, $("#login-password").value);
      render();
    } catch (err) {
      $("#login-error").textContent = err.message;
    }
  });

  $("#logout-btn").addEventListener("click", logout);

  $("#student-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    $("#student-error").textContent = "";
    try {
      await createStudent({
        first_name: $("#s-first").value,
        last_name: $("#s-last").value,
        student_number: $("#s-number").value,
        email: $("#s-email").value,
        program: $("#s-program").value,
      });
      e.target.reset();
      loadStudents();
    } catch (err) {
      $("#student-error").textContent = err.message;
    }
  });

  const saved = localStorage.getItem("token");
  if (saved) {
    state.token = saved;
    api("/api/auth/me")
      .then((u) => {
        state.user = u;
        render();
      })
      .catch(logout);
  }
});
