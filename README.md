# AI Student Support Agent

## Features
- Bounded tool-calling agent loop (model can request a tool, receives the result, then answers).
- SQLite records for 10 students, fees, scholarship statuses, two semester exam schedules and separate semester timetables.
- Academic calendar for holidays, co-curricular activities, fests and concerts. Calendar entries are **sample data**, not official notices.
- Six tools: fee lookup, scholarship lookup, support-ticket creation, exam schedule, semester/day timetable and academic calendar.
- Relevant handbook paragraph retrieval (lexical top-k); the whole handbook is not sent to the model.
- Persistent low-risk profile memory only: preferred name, programme and semester. Raw chat, temporary statements and sensitive details are not stored as long-term memory.
- Per-query JSON trace: tool calls, evidence headings, latency, token counts (from API usage where returned), status.
- Streamlit UI and offline component smoke tests.

## Setup (Windows PowerShell / VS Code terminal)
```powershell
cd path\to\ai_student_support_agent
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env` and add your Groq API key. Then:
```powershell
python setup_db.py
python demo_tests.py
streamlit run app.py
```
Open the local URL printed by Streamlit.

## Sample data notes
- `S1004` is the Mahi demo record, based on the supplied project context. All other student records are synthetic.
- Fee amounts, scholarship amounts/statuses, timetable and calendar are illustrative demo values. Confirm with the institution before real use.
- `policy_handbook.md` is a demonstration policy, not a real approved policy.
- The demo calendar explicitly labels provisional events and does not claim they are official.

## Privacy and production cautions
- This is a classroom prototype, not a production student information system.
- The demo does not implement login/identity verification. Do not deploy real student financial or scholarship records publicly.
- Before production: add institutional SSO, role-based authorization, audit controls, encryption, retention rules, approved policy documents, admin workflows and data validation.
- Session profile memory is keyed by the user-entered session ID and stored locally in `student_memory.json`. Use an authenticated identity in production.
- `traces.jsonl` stores question text and operational metadata; do not log sensitive questions in production without an approved retention/privacy policy.


## Required demonstration scenarios
1. **Fee status:** Ask `What is my current fee status? My student ID is S1004.` The agent should call `get_fee_status`; the seeded demo record returns total ₹223,000, paid ₹150,000 and pending ₹73,000.
2. **Payment portal failure:** Ask `The payment portal failed. Can I pay on the next working day?` The retriever supplies only the fee-payment policy section. The policy says no automatic extension; written Accounts Office confirmation is required. A ticket can be raised with `raise_support_ticket`.
3. **New session memory:** In one session ask `My name is Mahi.` Then restart the app or open the same session ID and ask `What name do you have for me?`. The low-risk preferred name is read from `student_memory.json`.
4. **Temporary/sensitive statement:** Share a temporary or sensitive detail. The agent does not persist raw chat; only an explicit preferred name/programme/semester can be saved, and sensitive-keyword checks reject storage.
5. **Insufficient policy evidence:** Ask about a rule absent from the handbook, such as swimming-pool hours. No matching evidence is retrieved; the agent should say the handbook does not specify rather than invent an answer.

## Tracing and measurement
Every call to `answer()` prints a `[TRACE]` JSON line and appends the same record to `traces.jsonl`. Fields include timestamp, query, tools used, retrieved handbook headings, latency, API-reported prompt/completion/total tokens and status. If the API provider does not return usage, token fields remain zero; they are not estimated. The Streamlit UI also displays the trace. `demo_tests.py` reports deterministic component accuracy and tool/retrieval latency. Its 100% result validates the included deterministic checks only; it is **not** a claim about live model response accuracy. Measure end-to-end answer accuracy by running a labelled question set against the live API and manually scoring each final answer against the seeded source records and handbook.
