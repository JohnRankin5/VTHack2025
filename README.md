# Fire Guard 🚒🔥
**Enhancing Safety, Communication, and Navigation for Firefighters**

Fire Guard is a smart firefighter helmet that fuses **LiDAR, radar, IMU, RGB camera, and microphone data** with **AI-powered perception and mapping**. It generates real-time SLAM and semantic maps, penetrates smoke where cameras fail, and transcribes speech to text for clear communication.

---

## ✨ Features
- **SLAM Mapping** → LiDAR + radar fusion for navigation in smoke-filled environments  
- **Semantic Mapping** → Object detection (YOLOv5) + LLM (DistilGPT-2) to classify rooms  
- **Communication** → Whisper for real-time speech-to-text transcription  
- **Sensor Fusion** → LiDAR (geometry), Radar (penetrative sensing), IMU (localization), Camera (CV)  
- **HUD Display** → Real-time awareness inside the helmet  

---

## 📖 Inspiration
As a past volunteer firefighter, one of our teammates experienced the challenges of **limited visibility, disorientation, and noisy radio communication** during real emergencies. Fire Guard was inspired by the idea that **better technology can save lives.**

---

## 🛠️ How We Built It
- **Sensors**  
  - LiDAR → 2D mapping  
  - Radar (24 GHz FMCW) → depth through smoke  
  - IMU → drift correction & localization  
  - RGB Camera → YOLOv5 object detection  
  - Microphone → Whisper speech-to-text  

- **AI Components**  
  - YOLOv5 → Object detection  
  - DistilGPT-2 → Room labeling via semantic mapping  
  - Whisper → Speech-to-text  

- **Networking**  
  - Custom ad-hoc router system over 802.11 Wi-Fi  
  - Multi-device data transfer via sockets and ports  

---

## 📚 What We Learned
- Multi-sensor fusion is powerful but challenging  
- Radar requires significant documentation and setup to configure properly  
- Lightweight LLMs can improve communication by labeling rooms  
- Real-time pipelines under hardware constraints push you to think creatively  

---

## ⚡ Challenges
- Radar setup: only worked on Windows due to driver limitations  
- Embedded constraints: Jetson TX2 Nano lacked proper support  
- Real-time fusion: combining multiple data streams under time pressure  
- Speech transcription in noisy environments  

---

## 🚀 Next Steps
- Port to a **newer Jetson Nano** for tighter integration  
- Optimize networking for **real-time field deployment**  
- Extend semantic mapping with more attributes (e.g., color, material)  
- Improve HUD for clearer real-time awareness  

---

## 📂 Repository Structure
