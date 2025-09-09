erDiagram
    SURVEYS {
        int survey_id PK "Primary Key"
        varchar title "e.g., 'Encuesta de Fumadores Activos'"
        int version "e.g., 1, 2"
        text description
        datetime created_at
    }

    QUESTIONS {
        int question_id PK "Primary Key"
        int parent_question_id FK "Links a matrix row to its parent question"
        varchar question_text "The actual question text"
        enum question_type "'SINGLE', 'MULTIPLE', 'MATRIX', 'TEXT'"
        boolean is_required
    }

    SURVEY_QUESTIONS {
        int survey_id PK, FK
        int question_id PK, FK
        int display_order "Order of question in the survey"
    }

    OPTIONS {
        int option_id PK "Primary Key"
        int question_id FK "Links option to a question"
        varchar option_text "e.g., 'Hombre', 'Mujer', 'Cafetería'"
    }

    OBSERVERS {
        int observer_id PK "Primary Key"
        varchar name "Observer's full name"
        varchar email
    }

    ZONES {
        int zone_id PK "Primary Key"
        varchar name "e.g., 'Zona 1', 'Campus Principal'"
        text description
    }

    SURVEY_SESSIONS {
        int session_id PK "Primary Key, represents one observer's assignment"
        int observer_id FK
        int zone_id FK
        int survey_id FK
        date start_date
        date end_date
        varchar photo_evidence_url "URL to Drive folder"
        varchar status "'IN_PROGRESS', 'COMPLETED'"
    }

    VISITS {
        int visit_id PK "Primary Key"
        int session_id FK "Links this visit to an observer's session"
        int visit_number "e.g., 1 through 6"
        date visit_date
        time start_time
        time end_time
    }

    ANSWERS {
        int answer_id PK "Primary Key"
        int visit_id FK "The visit where the answer was recorded"
        int question_id FK "The question being answered"
        int option_id FK "The specific option chosen (if applicable)"
        text answer_value "For text input or numerical matrix values"
    }

    %% --- Defining Relationships ---
    SURVEYS ||--o{ SURVEY_QUESTIONS : "has"
    QUESTIONS ||--o{ SURVEY_QUESTIONS : "belongs to"
    QUESTIONS ||--|{ OPTIONS : "has"
    QUESTIONS }o--o{ QUESTIONS : "can be parent of"
    OBSERVERS ||--|{ SURVEY_SESSIONS : "conducts"
    ZONES ||--|{ SURVEY_SESSIONS : "is assigned to"
    SURVEYS ||--|{ SURVEY_SESSIONS : "uses form"
    SURVEY_SESSIONS ||--|{ VISITS : "is composed of"
    VISITS ||--o{ ANSWERS : "contains"
    QUESTIONS ||--o{ ANSWERS : "is answered in"
    OPTIONS }o--o{ ANSWERS : "is selected for"
