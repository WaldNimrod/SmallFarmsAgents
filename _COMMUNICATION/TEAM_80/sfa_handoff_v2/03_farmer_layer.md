# Farmer Interaction Layer (Access Control)

## Goal
Enable advanced interaction ONLY for verified farmers

## Flow

1. Visitor sees:
- table (read-only)
- teaser: "התאם את הנתונים שלך"

2. Click → requires login

3. Registration form includes:
- checkbox: "אני חקלאי"

4. WordPress role flow:
- user registers
- default role: pending_farmer
- admin approves → role: farmer

5. Feature unlock:
- editable inputs
- save scenarios (future)

## UX Note
Before approval:
show disabled inputs + hint:
"זמין לחקלאים מאומתים"

---

## Roles

- guest → view only
- registered → limited
- farmer → full interaction
- admin → approve
