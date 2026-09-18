# Database Schema

```mermaid
erDiagram
    VENUES ||--o{ EVENTS : hosts

    VENUES {
        string venue_id PK
        string venue_name
        string city
        string state
    }

    EVENTS {
        string event_id PK
        string event_name
        string event_date
        string venue_id FK
    }