# Product Requirements Document (PRD): Chirp

**Project Name:** Chirp  
**Version:** 1.1  
**Status:** Implementation phase  
**Concept:** A smart, modular social media orchestrator using Gemini 1.5 Flash AI and Streamlit.

---

## 1. Project Vision
**Chirp** is designed to bridge the gap between content creation and scheduling. It acts as an intelligent assistant that helps users generate platform-optimized content, preview it in real-time, and manage a simulated posting lifecycle, specifically catering to non-technical users through simple CSV integrations and visual calendars.

## 2. Target Features

### 2.1 Content & AI Engine (Powered by Gemini 1.5 Flash)
*   **Brand Voice Modulation:** Users choose a tone (Professional, Gen-Z, Funny, Hype) which dynamically adjusts the Gemini AI prompt.
*   **Platform-Awareness:** The AI generates content tailored to specific platform constraints (Twitter, LinkedIn, Instagram, Facebook). Users can generate variations for multiple platforms simultaneously.
*   **Smart Scheduling:** A "Suggest Best Time" heuristic engine that recommends posting times based on platform-specific peak engagement data.
*   **Vision-Powered "Image-to-Caption" Generation:** Users can upload an image, and the AI will analyze the visual content to generate highly contextual, platform-specific captions based on the image itself.

### 2.2 Scheduling & Logic
*   **Conflict Detection:** A validation layer that prevents overlapping posts on the same platform.
*   **Status Lifecycle:** Automated transition from `Draft` → `Scheduled` → `Posted`.
*   **Bulk Import/Export:** Ability to upload or download a CSV file to schedule multiple posts simultaneously, acting as a portable content calendar.

### 2.3 UI & Analytics (Modular Streamlit App)
*   **Visual Content Calendar:** A visual calendar view in the dashboard displaying all upcoming scheduled posts in an easy-to-read monthly grid.
*   **Live Mobile Preview:** A real-time visual mockup showing how the post will look on a mobile device.
*   **Engagement Simulation:** Randomized "Performance Metrics" (Likes, Shares) generated once a simulated post moves to the "Posted" status.
*   **Interactive Dashboard:** Visual charts showing platform distribution and content volume.

---

## 3. Technical Architecture (Modular Package Design)

The project is structured into independent Python packages and Streamlit pages for strict modularity.

### Directory Structure
```text
chirp_project/
├── app.py                 # Main Orchestrator (Entry Point & Navigation)
├── models/                # Shared data structures
│   ├── __init__.py
│   ├── enums.py           # Platform, PostStatus, Tone
│   └── post.py            # SocialPost dataclass/pydantic model
├── ai/                    # AI & Prompt Engineering
│   ├── __init__.py
│   ├── generator.py       # Gemini API client (Text & Vision)
│   └── heuristics.py      # Time suggestion logic
├── storage/               # Persistence Layer (CSV Only)
│   ├── __init__.py
│   ├── local.py           # CSV file read/write handling
│   └── importer.py        # Bulk CSV calendar parsing
├── engine/                # Core Business Logic
│   ├── __init__.py
│   ├── validator.py       # Regex & Conflict checks
│   └── analytics.py       # Engagement simulation math
└── ui/                    # Presentation Layer
    ├── __init__.py
    ├── pages/             # Streamlit page modules (create.py, dashboard.py, settings.py)
    ├── components.py      # Reusable Streamlit widgets
    └── mockups.py         # Phone frame CSS/HTML
```

---

## 4. Constraints & Error Handling

### Regex Validation
* **Hashtag count check:** Ensure appropriate hashtag density per platform.
* **Link detection:** Warn users that links are non-clickable on platforms like Instagram.

### Exception Handling
* **ScheduleConflictError:** Custom exception for overlapping times.
* **AIConnectionError:** Fallback to manual entry if API is unreachable.
* **FileCorruptionError:** Graceful handling of missing or malformed CSV files.

---

## 5. Success Metrics for Review

* **Strict Modularity:** Can a package be swapped or updated without touching `app.py`?
* **Robustness:** Does the app survive invalid CSV uploads or empty form submissions?
* **User Experience:** Does the Live Preview and Content Calendar provide genuine value to the content creation process?
