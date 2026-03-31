# unknownapp
This is an unknown application written in Java

---- For Submission (you must fill in the information below) ----
### Use Case Diagram
![UseCase](images/usecase.png)

### Flowchart of the main workflow

```mermaid
flowchart TD
    A[Start Application] --> B[Initialize Data]
    B --> C[Display Login Menu]
    C --> |1 Student| D[Student Login]
    C --> |2 Admin| E[Admin Login]
    C --> |3 Exit| Z[Save and Exit]

    D --> |Existing Student| F[Student Menu]
    D --> |new| G[Create Student Profile]
    G --> F
    D --> |failed| C

    F --> |1 View Catalog| F
    F --> |2 Register Course| F
    F --> |3 Drop Course| F
    F --> |4 View Schedule| F
    F --> |5 Billing| F
    F --> |6 Edit Profile| F
    F --> |7 Logout and Save| C

    E --> |valid pwd| H[Admin Menu]
    E --> |invalid| C

    H --> |1 View Catalog| H
    H --> |2 View Roster| H
    H --> |3 View Students| H
    H --> |4 Add Student| H
    H --> |5 Edit Student| H
    H --> |6 Add Course| H
    H --> |7 Edit Course| H
    H --> |8 View Student Schedule| H
    H --> |9 Billing Summary| H
    H --> |10 Logout and Save| C

    Z --> I[End]
```

### Prompts
