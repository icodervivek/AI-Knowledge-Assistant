import os, json

os.makedirs("data/raw", exist_ok=True)

documents = [

    {
        "filename": "hr_policy.json",
        "content": """
        Employees are entitled to 20 paid leaves annually.
        Sick leave can be applied through the HR portal.
        Emergency leave requires manager approval.
        Work from home is allowed twice a week.
        """,
        "metadata": {
            "title": "HR Leave Policy",
            "tags": ["HR", "leave", "policy"],
            "type": "policy",
            "date": "2026-05-19"
        }
    },

    {  
    "filename": "company_overview.json",
    "content": """
    FloCard is a sustainability-focused digital business platform founded in India.
    The company provides digital business cards, sustainability solutions, and climate-focused business tools.
    FloCard helps businesses reduce paper waste while supporting sustainability and net-zero initiatives.
    The platform enables users to create secure digital business cards that can be shared through QR codes, li
    nks, and OTP-based access.
    FloCard also offers solutions such as carbon offsetting, GHG calculators, SDG alignment, climate finance support, and sustainability dashboards.
    The company promotes the #BetterPlanetTogether initiative to encourage organizations and individuals to contribute toward global sustainability goals.
    FloCard supports businesses in aligning with the United Nations Sustainable Development Goals (SDGs) and climate action programs.
    The platform focuses on combining networking, environmental responsibility, and digital transformation into a unified ecosystem.
    FloCard operates through business, community, and sustainability-driven initiatives across multiple sectors.
    """,
    "metadata": {
        "title": "Company Overview",
        "tags": ["company", "overview", "flocard", "sustainability", "digital-business-card"],
        "type": "overview",
        "date": "2026-05-20"
    }
    },

    {
        "filename": "team_faq.json",
        "content": """
        Q: How do I request access to internal tools?
        A: Submit a request via the IT portal at ask@flocard.app. Approval takes 1-2 business days.

        Q: Who do I contact for payroll issues?
        A: Reach out to ask@flocard.app or raise a ticket in the HR portal under the Payroll section.

        Q: How do I join the engineering on-call rotation?
        A: Speak to your team lead. On-call rotations are managed in PagerDuty and shifts are weekly.

        Q: Where can I find the company org chart?
        A: The org chart is available on the internal Confluence page under Company > People > Org Chart.

        Q: What is the process for getting a new laptop?
        A: New hardware requests must be approved by your manager and submitted via the IT portal.

        Q: How do I reset my VPN credentials?
        A: Contact the IT helpdesk at ask@flocard.app.
        """,
        "metadata": {
            "title": "Team FAQ",
            "tags": ["FAQ", "team", "HR", "IT", "onboarding"],
            "type": "faq",
            "date": "2026-05-19"
        }
    },

    {
        "filename": "api_guide.json",
        "content": """
        FloCard Internal API Guide

        Base URL: https://api.flocard.internal/v2

        Authentication:
        All API requests require a Bearer token in the Authorization header.
        Example: Authorization: Bearer <your_token>
        Tokens can be generated from the Developer Portal at dev.flocard.internal.

        Common Endpoints:

        GET /expenses
        Returns a paginated list of expense records for the authenticated user.
        Query params: page (int), limit (int, max 100), status (pending|approved|rejected)

        POST /expenses
        Creates a new expense entry.
        Body: { "amount": 500, "currency": "INR", "category": "travel", "description": "Client meeting cab" }

        POST /expenses/{id}/approve
        Approves a pending expense. Requires manager role.

        GET /reports/summary
        Returns a spending summary grouped by category for the current month.

        Error Codes:
        400 - Bad Request: missing or invalid fields
        401 - Unauthorized: invalid or expired token
        403 - Forbidden: insufficient permissions
        404 - Not Found: resource does not exist
        500 - Internal Server Error: contact the platform team
        """,
        "metadata": {
            "title": "FloCard API Developer Guide",
            "tags": ["API", "developer", "engineering", "integration"],
            "type": "tutorial",
            "date": "2026-05-19"
        }
    },

    {
        "filename": "dev_setup.json",
        "content": """
        Local Development Environment Setup

        Prerequisites:
        - Node.js v20 or higher
        - Python 3.11 or higher
        - Docker Desktop
        - Git configured with your FloCard email

        Step 1: Clone the repository
        git clone git@github.com:flocard/platform.git
        cd platform

        Step 2: Install backend dependencies
        cd server
        python -m venv venv
        venv/Scripts/activate  (Windows) or source venv/bin/activate (Mac/Linux)
        pip install -r requirements.txt

        Step 3: Install frontend dependencies
        cd ../client
        npm install

        Step 4: Set up environment variables
        Copy .env.example to .env and fill in required values.
        Ask your team lead for the development API keys.

        Step 5: Start local services
        docker-compose up -d   (starts PostgreSQL and Redis)

        Step 6: Run the backend
        cd server
        uvicorn api.main:app --reload --port 8000

        Step 7: Run the frontend
        cd client
        npm run dev

        The app will be available at http://localhost:3000.
        API docs are at http://localhost:8000/docs.
        """,
        "metadata": {
            "title": "Developer Environment Setup Guide",
            "tags": ["engineering", "setup", "development", "tutorial"],
            "type": "tutorial",
            "date": "2026-05-19"
        }
    },

    {
        "filename": "onboarding_sop.json",
        "content": """
        New Employee Onboarding SOP

        This document describes the standard onboarding process for all new FloCard employees.

        Week 1 — Setup and Orientation
        Day 1: Collect your laptop from IT. Set up email, Slack, and VPN access.
        Day 2: Complete mandatory compliance and security training in the LMS portal.
        Day 3: Meet your buddy (assigned by HR) and attend the company orientation session.
        Day 4-5: Shadow your team and review relevant internal documentation.

        Week 2 — Role Onboarding
        Engineering hires: Set up local dev environment using the Dev Setup Guide.
        Complete your first small task or bug fix with code review from your team lead.
        Non-engineering hires: Complete role-specific training modules in the LMS.

        Checklists:
        - IT access provisioned (email, Slack, GitHub, Jira)
        - HR documents signed (NDA, employment contract, POSH policy)
        - First 30-60-90 day goals set with manager
        - Added to team Slack channels and calendar invites

        Contacts:
        HR queries: ask@flocard.app
        """,
        "metadata": {
            "title": "New Employee Onboarding SOP",
            "tags": ["onboarding", "SOP", "HR", "process"],
            "type": "sop",
            "date": "2026-05-19"
        }
    },

    {
        "filename": "code_review_sop.json",
        "content": """
        Code Review Standard Operating Procedure

        Purpose:
        To ensure all code changes meet FloCard quality and security standards before merging.

        Rules:
        1. Every pull request must have at least 2 approvals before merging.
        2. No self-merges are allowed, even for urgent hotfixes.
        3. All CI checks (lint, tests, security scan) must pass before review can be approved.
        4. PRs should be kept small — ideally under 400 lines of change.
        5. Reviewers must respond within 1 business day.

        What reviewers must check:
        - Correctness: Does the code do what the PR description says?
        - Security: No hardcoded secrets, no SQL injection risks, no exposed PII.
        - Tests: Are unit and integration tests added or updated?
        - Documentation: Are new functions and APIs documented?
        - Performance: No obvious N+1 queries or blocking operations on the main thread.

        How to raise a PR:
        1. Push your branch to origin.
        2. Open a PR on GitHub with a clear title and description.
        3. Tag relevant reviewers and link the Jira ticket.
        4. Address all review comments before re-requesting review.

        Hotfix process:
        For production incidents, one approval is sufficient but the second must follow within 24 hours.
        All hotfixes must be accompanied by a post-mortem ticket in Jira.
        """,
        "metadata": {
            "title": "Code Review SOP",
            "tags": ["engineering", "SOP", "process", "code review", "best practices"],
            "type": "sop",
            "date": "2026-05-19"
        }
    },

]


for document in documents:

    path = f"data/raw/{document['filename']}"

    with open(path, "w", encoding="utf-8") as file:

        json.dump(
            {
                "content": document["content"],
                "metadata": document["metadata"]
            },
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"Generated: {path}")

print(f"\nDone. {len(documents)} synthetic documents generated in data/raw/")
