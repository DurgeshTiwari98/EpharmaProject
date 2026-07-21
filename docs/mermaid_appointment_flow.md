# Appointment Flow Sequence Diagram

```mermaid
sequenceDiagram
    actor Patient
    participant App
    participant Doctor
    participant Consultation
    participant Prescription

    Patient->>App: Search doctor/specialty
    Patient->>App: Select slot and book
    App->>Doctor: Appointment request
    Doctor-->>App: Accept or reject
    App-->>Patient: Confirmation
    Patient->>Consultation: Join chat/video
    Doctor->>Consultation: Complete consultation
    Doctor->>Prescription: Create e-prescription
    Prescription-->>Patient: Prescription available
    Prescription-->>App: Medicine order recommendations
```
