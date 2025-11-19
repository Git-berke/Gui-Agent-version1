# 🤖 GUI Agent - Version 1

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-prototype-orange)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📢 TUBITAK 2209 Acknowledgement / Teşekkür

> 🇬🇧 **English:**
> This project is developed as a **prototype** structure within the scope of the **TÜBİTAK 2209 Undergraduate Research Projects Support Program**. It serves as a foundational framework for research and development in GUI-based AI agents.

> 🇹🇷 **Türkçe:**
> Bu proje, **TÜBİTAK 2209 Üniversite Öğrencileri Araştırma Projeleri Destekleme Programı** kapsamında **prototip** bir yapı olarak geliştirilmiştir. GUI tabanlı yapay zeka ajanları üzerine yapılan araştırma ve geliştirme çalışmaları için temel bir çerçeve niteliği taşımaktadır.

---

## 📂 Project Structure / Proje Yapısı

The project follows a modular architecture designed for scalability and separation of concerns.
Proje, ölçeklenebilirlik ve görevlerin ayrılması için modüler bir mimari izler.

```
Gui-Agent-version1/
├── main.py                  # 🚀 Entry point of the application / Uygulama giriş noktası
├── requirements.txt         # 📦 Dependencies / Bağımlılıklar
├── prompts/                 # 📝 System prompts & configurations / Sistem promptları
│   └── system.yaml
├── src/                     # 🧠 Source Code / Kaynak Kodlar
│   ├── agent/               # Core agent logic (decision making) / Ajan mantığı
│   ├── perception/          # Input processing (vision/GUI analysis) / Algılama modülü
│   ├── memory/              # Context & history management / Hafıza yönetimi
│   ├── mcp_server/          # Model Context Protocol server / MCP sunucusu
│   └── utils/               # Helper functions / Yardımcı araçlar
└── ...
```

---

## 🇬🇧 English Documentation

### Architecture Overview
This prototype implements an autonomous agent capable of interacting with Graphical User Interfaces (GUI). The system is divided into distinct components:

1.  **Agent Core (`src/agent`):** The "brain" of the system. It orchestrates the workflow, deciding which actions to take based on inputs from the perception module and current memory state.
2.  **Perception (`src/perception`):** Responsible for "seeing" or understanding the environment. It processes inputs (likely screenshots or accessibility trees) to provide structured data to the agent.
3.  **Memory (`src/memory`):** Manages the state. It keeps track of past actions, current context, and user instructions to ensure continuity.
4.  **MCP Server (`src/mcp_server`):** Implements a server compatible with the Model Context Protocol, allowing standardized communication between the AI model and the toolset.

### 🚀 How to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Git-berke/Gui-Agent-version1.git
    cd Gui-Agent-version1
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Agent:**
    ```bash
    python main.py
    ```

---

## 🇹🇷 Türkçe Dokümantasyon

### Mimari Genel Bakış
Bu prototip, Grafiksel Kullanıcı Arayüzleri (GUI) ile etkileşime girebilen otonom bir ajan uygulamasıdır. Sistem, her biri belirli bir görevi üstlenen ayrık bileşenlere bölünmüştür:

1.  **Agent Core (`src/agent`):** Sistemin "beyni". Algılama modülünden gelen girdilere ve mevcut hafıza durumuna dayanarak hangi aksiyonların alınacağına karar verir ve iş akışını yönetir.
2.  **Perception (`src/perception`):** Ortamı "görmekten" veya anlamaktan sorumludur. Girdileri (ekran görüntüleri veya erişilebilirlik ağaçları) işleyerek ajana yapılandırılmış veri sağlar.
3.  **Memory (`src/memory`):** Durum yönetimini sağlar. Sürekliliği sağlamak için geçmiş eylemleri, mevcut bağlamı ve kullanıcı talimatlarını takip eder.
4.  **MCP Server (`src/mcp_server`):** Model Bağlam Protokolü (Model Context Protocol) ile uyumlu bir sunucu uygulayarak, yapay zeka modeli ile araç seti arasında standartlaştırılmış bir iletişim sağlar.

### 🚀 Nasıl Çalıştırılır

1.  **Repoyu klonlayın:**
    ```bash
    git clone https://github.com/Git-berke/Gui-Agent-version1.git
    cd Gui-Agent-version1
    ```

2.  **Gerekli kütüphaneleri yükleyin:**
    Sanal ortam (virtual environment) kullanılması önerilir.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Uygulamayı başlatın:**
    ```bash
    python main.py
    ```

---

<div align="center">

**Developed for TÜBİTAK 2209**
*Gui-Agent v1 Prototype*

</div>

