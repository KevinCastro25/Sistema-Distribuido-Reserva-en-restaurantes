const API_URL = "http://127.0.0.1:5000/clientes";

// =======================
// Login
// =======================
document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  try {
    const response = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    if (response.ok) {
      alert("Inicio de sesión exitoso");
      localStorage.setItem("token", data.token); // Guardar JWT
      window.location.href = "/reservas/"; // redirigir al módulo reservas
    } else {
      alert("Error: " + data.message);
    }
  } catch (error) {
    console.error("Error en login:", error);
    alert("Error de conexión con el servidor");
  }
});

// =======================
// Registro
// =======================
document.getElementById("registerForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const nombre = document.getElementById("regNombre").value;
  const email = document.getElementById("regEmail").value;
  const password = document.getElementById("regPassword").value;

  try {
    const response = await fetch(`${API_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre, email, password })
    });

    const data = await response.json();
    if (response.ok) {
      alert("Usuario registrado correctamente 🎉");
    } else {
      alert("Error: " + data.message);
    }
  } catch (error) {
    console.error("Error en registro:", error);
    alert("Error de conexión con el servidor");
  }
});

// =======================
// Redirección al back office
// =======================
function redirigirAdmin() {
  window.location.href = "/admin/login";
}