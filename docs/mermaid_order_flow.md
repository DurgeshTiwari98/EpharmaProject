# Order Flow Sequence Diagram

```mermaid
sequenceDiagram
    actor Patient
    participant App
    participant Catalog
    participant Pharmacy
    participant Payment
    participant Delivery

    Patient->>App: Search medicine
    App->>Catalog: Query active SKUs and stock
    Catalog-->>App: Medicine results
    Patient->>App: Add items to cart
    Patient->>App: Checkout
    App->>Payment: Initiate payment
    Payment-->>App: Payment success/failure
    App->>Pharmacy: Create paid order
    Pharmacy->>Pharmacy: Pick and pack order
    Pharmacy->>Delivery: Dispatch order
    Delivery-->>App: Delivery status updates
    App-->>Patient: Order tracking and invoice
```
