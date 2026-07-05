# Data Minimization Checklist

| Data | Needed for MVP | Keep? | Note |
| :--- | :--- | :--- | :--- |
| Username | yes | yes | Demo identifier. |
| Password hash | yes for auth shape | yes | Never store plaintext passwords. |
| Habit title | yes | yes | Core product data. |
| Habit category | yes | yes | Used for UI grouping. |
| Check-in timestamp | yes | yes | Needed for same-day check-in rule. |
| Email | no | no | Not part of current demo. |
| Payment data | no | no | Never collect for this checkpoint. |
| Precise location | no | no | Not needed. |

## Review rule

Before adding a field, ask:

1. Which user action requires it?
2. Can the product work without it?
3. How will the user delete or correct it?
4. Could it expose private behavior if logged?
