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
// Config Firebase
// =======================
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/11.0.0/firebase-auth.js";

// Configuración de Firebase (usa exactamente los valores de tu proyecto)
const firebaseConfig = {
  apiKey: "AIzaSyCuQhjKG3LqaQRHV3L3WN5sZJH8O0_yQwc",
  authDomain: "reservasrest-a3af5.firebaseapp.com",
  projectId: "reservasrest-a3af5",
  storageBucket: "reservasrest-a3af5.firebasestorage.app",
  messagingSenderId: "932026827790",
  appId: "1:932026827790:web:7bb9f45dbe29ad8405285f",
  measurementId: "G-D94BPY9RSK"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

// =======================
// Login con Google
// =======================
document.getElementById("googleLoginBtn").addEventListener("click", async () => {
  try {
    // Login con Firebase
    const result = await signInWithPopup(auth, provider);
    const idToken = await result.user.getIdToken(); // 🔑 token de Google

    // Mandar token a tu backend
    const response = await fetch(`${API_URL}/google-login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: idToken })
    });

    const data = await response.json();
    if (response.ok) {
      alert("Inicio de sesión con Google exitoso");
      localStorage.setItem("token", data.token); // tu JWT
      window.location.href = "/reservas/";
    } else {
      alert("Error: " + data.message);
    }
  } catch (error) {
    console.error("Error en login con Google:", error);
    alert("No se pudo iniciar sesión con Google");
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
  window.location.href = "http://127.0.0.1:5000/admin/login"; 
}