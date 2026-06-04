# PestPatrol: UAV-Based Corn Pest Monitoring System Utilizing Multimodal Model

PestPatrol is a comprehensive, cost-effective Unmanned Aerial Vehicle (UAV) monitoring system designed to detect and calculate the population density of nocturnal corn pests using high-resolution RGB imagery and a multimodal artificial intelligence model. 

## Project Overview

In the Philippines, declining maize production is exacerbated by rising nocturnal pest infestations, such as the Fall Armyworm, Asian Corn Borer, and Corn Earworm. Traditional manual monitoring is time-consuming and prone to errors. PestPatrol addresses this gap by offering a scalable, automated nighttime monitoring solution tailored for smallholder farmers. By leveraging affordable UAVs equipped with RGB cameras and the Gemini 2.5 Pro multimodal model, the system identifies pests and calculates population density, empowering farmers with real-time, data-driven insights for precision agriculture interventions. 

### Key Features

* **Automated Nighttime UAV Surveys:** Pre-programmed flight waypoint execution ensuring precise field coverage. 


* **Real-Time RTMP Livestreaming:** Low-latency aerial footage delivery from the UAV to the ground control server over Wi-Fi or mobile networks. 


* **Multimodal AI Pest Detection:** Utilizes Gemini 2.5 Pro to accurately detect pests under low-light conditions, even when partially occluded. 


* **Modified Pest Population Density Calculation:** Implements a refined mathematical model that factors in AI detection confidence levels for superior accuracy. 


* **Interactive Web GUI:** Intuitive dashboards for livestreaming, history tracking, farm details, and recommended actions. 



---

## System Architecture

### Hardware Layer

* **UAV Platform:** A drone capable of autonomous waypoint navigation and maintaining set cruising speeds and altitudes. 


* **UAV Camera:** A high-resolution RGB camera mounted on a configurable gimbal for capturing nighttime imagery at specific angles of elevation. 


* **Communication Modules:** Wi-Fi and mobile internet data connectivity modules for streaming video and transmitting API payloads. 


* **Web Server:** A local or cloud-based server infrastructure running NGINX to handle high-traffic RTMP video streaming. 



### Software Layer

* **Flight Planning Application:** The Litchi app is utilized to configure waypoints and manage autonomous flight operations. 


* **Backend Processing:** A Python-based server (`app.py`) processes the incoming RTMP stream and orchestrates data logic. 


* **Multimodal Model API:** Google AI Studio's Gemini 2.5 Pro API serves as the core engine for image analysis and pest identification. 


* **Frontend GUI:** A responsive web interface allowing end-users to view live video, access historical data, and monitor specific farm profiles. 



---

## Hardware Components

| Component | Purpose | Description |
| --- | --- | --- |
| **UAV (Drone)** | Aerial Navigation | Follows pre-set flight plans over corn fields to gather visual data. 

 |
| **RGB Camera** | Visual Data Acquisition | Captures high-resolution nighttime imagery; serves as an affordable alternative to multispectral sensors. 

 |
| **Litchi App Host Device** | Flight Control | Laptop or mobile device used to set up, calibrate, and monitor automated UAV waypoints. 

 |
| **Web Server Machine** | Processing Hub | Receives RTMP streams, communicates with the AI API, and serves the GUI to end-users. 

 |

## Software Components

| Component | Description | Module Purpose |
| --- | --- | --- |
| **`app.py`** | Application Backend | Handles server initialization, stream processing, API requests to the multimodal model, and density calculations. 

 |
| **Gemini 2.5 Pro** | Multimodal AI Model | Processes streamed frames to execute object detection tasks (identifying pests based on size, orientation, and localization). 

 |
| **HTML Views** | Frontend Interfaces | Renders the GUI, including dashboards for livestreams, history logs, and farm overviews. 

 |
| **NGINX** | Streaming Protocol Server | Manages high-traffic, low-latency video delivery from the UAV via RTMP. 

 |

---

## Repository Structure

Based on the project's repository, the files are structured as follows:

```text
PestPatrol/
├── app.py             # Main backend application script handling routing, API calls, and logic.
├── index.html         # Application landing page or base template.
[cite_start]├── home.html          # GUI Home Page summarizing features and navigation. [cite: 116]
[cite_start]├── livestream.html    # GUI displaying real-time drone footage and immediate pest data. [cite: 117]
[cite_start]├── history.html       # GUI presenting past monitoring results and trend analysis. [cite: 118]
[cite_start]├── farms.html         # GUI providing specific farm details (size, ownership). [cite: 119]
[cite_start]├── about.html         # GUI sharing project objectives, methods, and team background. [cite: 120]
└── README.md          # Project documentation.

```

---

## System Workflow

1. **Setup and Calibration:** Configure the UAV and define the flight mission using the Litchi app. 


2. **Flight Execution:** The UAV autonomously surveys the corn field, capturing aerial footage. 


3. **Data Transmission:** Video data is live-streamed from the UAV camera to the Web Server using the RTMP protocol over Wi-Fi/Internet. 


4. **AI Inference:** The Web Server sends image frames via HTTP requests to the Gemini 2.5 Pro Multimodal Model for pest detection. 


5. **Density Calculation:** The system computes the pest population density utilizing the modified mathematical formula. 


6. **Data Output:** The processed data, highlighting high-density zones and recommended actions, is displayed on the end-user GUI. 


7. **Mission Completion:** The UAV returns to its home location once all pre-set waypoints are achieved. 



---

## Technology Stack

### Frontend

* HTML5
* CSS / JavaScript (Assumed standard web presentation layers)

### Backend

* Python (`app.py`)
* NGINX (RTMP Streaming Handling) 



### Artificial Intelligence

* Google Gemini 2.5 Pro (Multimodal Model) 



### Communication Protocols

* RTMP (Real-Time Messaging Protocol) 


* HTTP/REST (For Google Cloud Platform API integrations) 



---

## Mathematical Models

The system evaluates pest density using two formulas. The modified formula incorporates the model's confidence level to minimize deviation and errors.

**Base Population Density Formula:** 

$$D = \frac{N}{A}$$



**Modified Population Density Formula:** 

$$D = \frac{N}{A} \times C_{ave}$$



*Where:*

* $N =$ Total number of pests detected 


* $A =$ Area covered during the UAV survey in square meters 


* $C_{ave} =$ Average Confidence Level from a single detection operation 



---

## Installation Guide

### Prerequisites

* Python 3.8+
* NGINX compiled with the RTMP module.
* A Google Cloud Platform account to generate API keys. 



### 1. Clone Repository

```bash
git clone https://github.com/Jan-Ric/PestPatrol.git
cd PestPatrol

```

### 2. Environment Variables

Create a `.env` file in the root directory and configure the following parameters:

```env
# Google AI Studio configurations
GEMINI_API_KEY=your_google_cloud_api_key_here

# RTMP Stream URL
STREAM_URL=rtmp://your_server_ip/live/stream

```

*Note: Ensure the Gemini 2.5 Pro API is enabled in your Google Cloud Console and API keys are rotated regularly for security.* 

### 3. Running the Project

Start the backend server to serve the application and listen for RTMP streams.

```bash
python app.py

```

Open a web browser and navigate to `http://localhost:5000` (or the configured port) to access `index.html`.

---

## Data Flow Diagram

```text
UAV Camera 
  [cite_start]↓ (RTMP Protocol over Wi-Fi/Internet) [cite: 106]
NGINX Web Server
  [cite_start]↓ (HTTP Request) [cite: 96]
[cite_start]Google Gemini 2.5 Pro API (Pest Detection) [cite: 95]
  [cite_start]↓ (HTTP Response - Total Pest Count & Confidence Level) [cite: 135, 137]
[cite_start]Density Calculation Engine (Modified Formula) [cite: 129]
  ↓ 
[cite_start]Frontend GUI (Livestreaming, History, Actions) [cite: 117, 118]
  ↓
[cite_start]End-User Dashboard [cite: 89]

```

---

## Design Decisions

* **RGB Imagery over Multispectral:** Selected for affordability. It makes automated nighttime pest monitoring highly cost-effective and scalable for smallholder farmers with resource constraints. 


* **Angle of Elevation Optimization:** The UAV camera angle significantly impacts the field of view and the model's ability to distinguish pests from the background, especially in low light or partial occlusion. 


* **Integration of Average Confidence Level ($C_{ave}$):** Modifying the traditional density formula by multiplying it by the AI's confidence level generated a Root Mean Square Error (RMSE) of 0.1701, proving to be a highly reliable approach to minimizing error in wild deployment settings. 



## Future Improvements

* **Cruising Speed Optimization:** Statistical analysis (ANOVA) indicates that cruising speed configurations may require slight improvements to reduce slight residual deviations at higher values during inference time testing. 


* **Scale of Farm Support:** Expanding the farm database configuration to support larger commercial farm inputs alongside smallholder configurations. 


## Contributors

* Jan Ric M. Hogat 
* Clarence Joseph M. Gavina 
* Christine H. Ignacio 
* Jana Rose A. Bongalon 
* Natalia Paula Yemena B. Gavilan 
* Marife A. Rosales *(Polytechnic University of the Philippines)* 
