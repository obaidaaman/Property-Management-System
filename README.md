# Property Maintenance Management System

A mobile-first property maintenance management system that allows tenants to report issues, managers to assign technicians, and technicians to resolve maintenance tasks efficiently.

This project demonstrates backend architecture, workflow design, role-based access control, and Firestore-based ticket lifecycle management.

---

## Overview

Property managers often handle maintenance requests across multiple buildings using scattered tools like WhatsApp, spreadsheets, and emails.
This system centralizes the workflow into a single structured platform.

The application supports three roles:

* Tenant
* Property Manager
* Technician

Each role has controlled permissions and responsibilities.

---

## Features

### Authentication & Authorization

* JWT-based authentication
* Role-based access control
* Tenant / Manager / Technician permissions

---

### Ticket Management

Tenants can:

* Create maintenance tickets
* Upload images
* Provide title, description, and priority

Managers can:

* View all tickets
* Assign technicians
* Filter tickets
* Track activity logs

Technicians can:

* View assigned tickets
* Update ticket progress

---

### Ticket Workflow

The system enforces a strict status flow:

```
Open → Assigned → In Progress → Done
```

Transitions are validated to ensure:

* Managers assign tickets
* Technicians update progress
* Invalid state transitions are prevented

---

### Activity Logs

Each ticket maintains a full activity history:

* Ticket created
* Assignment events
* Status changes
* Comments

Logs are stored as a Firestore subcollection:

```
tickets/{ticket_id}/activity_logs
```

---

### File Upload Support

Tickets support image attachments via stored URLs.

---

### Manager Filtering

Managers can filter tickets using query parameters:

* status
* priority

Example:

```
GET /ticket/get-tickets?status=Open
```

---

## Tech Stack

Backend:

* FastAPI
* Firestore (Firebase Admin SDK)
* Pydantic
* JWT Authentication

Database:

* Google Firestore

Architecture:

* Router → Controller → Database
* Modular feature-based structure

---

## Project Structure

```
src/
 ├── auth/
 ├── users/
 ├── tickets/
 ├── files/
 ├── utils/
 └── main.py
```

Each module contains:

* router
* controller
* models

---

## API Endpoints

### Tickets

```
POST   /ticket/create-ticket
PATCH  /ticket/update-ticket/{ticket_id}
GET    /ticket/get-tickets
POST   /ticket/assign-tickets
GET    /ticket/{ticket_id}/activity
```

### Authentication

```
POST /auth/login
POST /auth/register
```

---

## Firestore Schema

### users

```
email
full_name
role
block_name
unit_number
phone_number
created_at
```

### tickets

```
user_id
title
description
priority
images
status
assigned_to
block_name
unit_number
created_at
updated_at
```

### activity_logs

```
type
content
user_id
user_role
created_at
```

---

## Running the Project

Install dependencies:

```
pip install -r requirements.txt
```

Run server:

```
uvicorn src.main:app --reload
```

---

## Design Decisions

This project focuses on:

* Clean backend architecture
* Role-aware workflow logic
* Firestore-optimized data model
* Activity logging for traceability
* Production-style ticket lifecycle validation

The goal is clarity and correctness rather than UI complexity.

---


---

## Author

Aman
