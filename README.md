# 🌱 AgriPulse — Digital Agriculture Interoperability Network

**AgriPulse** is an open-access Digital Public Good designed to empower farmers with real-time agronomic intelligence, computer-vision pathology diagnostics, and localized regenerative farming advisories delivered directly to field devices.

---

## 🚀 Key Features

* **🛰️ Real-Time Environmental Telemetry:** Ingests live ambient temperature, relative humidity, and surface soil moisture ($0\text{--}7\text{ cm}$) using the Open-Meteo API.
* **🔬 AI Crop Pathology Diagnostics:** Rapid plant leaf disease detection using Hugging Face vision models (`MobileNetV2`).
* **🧠 3-Step Regenerative Advisory Engine:** Generates hyper-localized, actionable biological management practices powered by Groq (LLaMA 3.1).
* **📱 WhatsApp Field Delivery:** Integrated with Meta WhatsApp Cloud API to allow farmers to send crop photos and receive instant diagnosis and advisories directly in chat.
* **✨ Real-Time Telemetry Dashboard:** Interactive frontend built with React, Vite, Tailwind CSS, and Framer Motion.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, FastAPI, Uvicorn, Pydantic |
| **Frontend** | React, Vite, Tailwind CSS, Lucide Icons, Framer Motion |
| **AI / ML** | Groq (LLaMA 3.1), Hugging Face Inference API |
| **Telemetry** | Open-Meteo Weather & Soil API |
| **Messaging** | Meta WhatsApp Cloud API (Graph API v20.0) |
| **Deployment** | Render (Backend Web Service), Vercel (Frontend) |

---

## 📡 API Endpoints

* `GET /health` — Health check endpoint.
* `GET /environment?lat={lat}&lon={lon}` — Returns real-time ambient temperature and soil moisture.
* `POST /diagnose` — Accepts plant leaf image upload and returns disease classification predictions.
* `POST /generate-advisory` — Generates a 3-step regenerative farming strategy based on crop health and live soil telemetry.
* `GET & POST /whatsapp-webhook` — Meta WhatsApp Cloud API challenge verification and incoming message handler.
