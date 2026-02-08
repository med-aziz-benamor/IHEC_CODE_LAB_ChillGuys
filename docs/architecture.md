# Architecture Overview

This document provides a high-level architecture view of the BVMT Trading Assistant.

```mermaid
flowchart TB
    %% User Interaction Layer
    U["Utilisateur\n(Web/Mobile)"]:::user

    %% Presentation Layer
    UI["Streamlit Dashboard"]:::ui
    API["REST API"]:::ui

    %% Application Layer
    PM["Portfolio Manager"]:::app

    %% Integration Layer
    DE{"Decision Engine"}:::decision

    %% Processing Layer
    F["Forecasting Module"]:::process
    S["Sentiment Module"]:::process
    A["Anomaly Module"]:::process
    T["Technical Indicators"]:::process

    %% Data Layer
    CSV[("CSV Files")]
    DL["Data Loader"]:::process

    %% Data Flow
    CSV --> DL
    DL --> F
    DL --> S
    DL --> A
    DL --> T

    F --> DE
    S --> DE
    A --> DE
    T --> DE

    DE --> PM
    DE --> UI
    DE --> API

    PM --> UI
    PM --> API

    U --> UI
    U --> API

    %% Styles
    classDef data fill:#e0f7fa,stroke:#00796b,color:#004d40;
    classDef process fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;
    classDef decision fill:#fff3e0,stroke:#ef6c00,color:#e65100;
    classDef ui fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c;
    classDef app fill:#e3f2fd,stroke:#1565c0,color:#0d47a1;
    classDef user fill:#fafafa,stroke:#9e9e9e,color:#424242;

    class CSV data;
```

```mermaid
flowchart LR
    F40["Forecast (40%)"]:::process
    S30["Sentiment (30%)"]:::process
    A20["Anomaly (20%)"]:::process
    T10["Technical (10%)"]:::process

    W["Weighted Scoring"]:::decision
    O["BUY / SELL / HOLD"]:::ui

    F40 --> W
    S30 --> W
    A20 --> W
    T10 --> W
    W --> O

    classDef process fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;
    classDef decision fill:#fff3e0,stroke:#ef6c00,color:#e65100;
    classDef ui fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c;
```

## Legend

- **Cylinders**: Data sources (CSV files)
- **Rectangles**: Processing modules (Forecasting, Sentiment, Anomaly, Technical, Data Loader)
- **Diamonds**: Decision points (Decision Engine, Weighted Scoring)
- **Rounded rectangles**: User interfaces (Streamlit Dashboard, REST API)
- **Solid arrows**: Data and signal flow between layers
