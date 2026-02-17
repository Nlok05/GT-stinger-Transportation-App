# 🚁 Georgia Tech Campus Drone Delivery Platform

A full-stack, AI-enhanced campus food delivery simulation built using Python and Streamlit.  
This application models a real-time drone-based delivery system with live geospatial tracking, ordering functionality, AI assistance, feedback analysis, and administrative analytics.

---

## Overview

The Campus Drone Delivery Platform simulates a university-wide autonomous drone delivery ecosystem.

Students can:
- Place food orders from campus restaurants
- Track deliveries on a live interactive map
- Chat with an AI assistant
- Submit categorized service feedback

Administrators can:
- Monitor active deliveries
- Analyze feedback using AI-generated summaries
- Track service metrics in real time
- Export operational reports

This project demonstrates end-to-end application design, real-time state management, and AI integration within a service-based platform.

---

## Key Features

### 🚁 Live Delivery Tracking
- Interactive 3D geospatial map powered by PyDeck
- Real-time simulated drone movement
- Visual route rendering between restaurants and delivery points
- Dynamic order status transitions (Preparing → In Transit → Delivered)
- Estimated Time of Arrival (ETA) calculation
- Auto-refresh for live simulation

### 🍽 Food Ordering System
- Restaurant and menu selection
- Cart management with quantity tracking
- Automatic price calculation
- Delivery location selection
- Simulated order placement
- Route preview after checkout

### 🤖 AI Assistant
- Built-in chat interface
- Persistent session-based conversation history
- AI-generated responses to user queries

### 📝 Feedback Management
- Structured feedback submission form
- AI-based priority classification (High / Medium / Low)
- AI-generated summaries and recommendations
- Admin visibility into issue trends

### 📊 Administrative Dashboard
- Real-time service analytics
- Active drone tracking
- Order volume monitoring
- Feedback statistics
- Status management (Resolved / In Progress)
- Exportable reports (JSON / TXT)

---

## Technical Architecture

**Primary Language**
- Python

**Framework**
- Streamlit

**Libraries**
- Pandas (data handling)
- PyDeck (geospatial visualization)
- JSON (data export)
- Datetime / Time (delivery lifecycle simulation)

**Frontend Rendering**
- Streamlit-generated HTML/CSS components

**State Management**
- Streamlit session state for real-time data persistence

---

## Project Structure
```txt
.
├── APP.py            # Main Streamlit application
├── requirements.txt  # Dependencies
└── README.md         # Documentation
