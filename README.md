# Enterprise AI Router

Enterprise AI Router is an AI-powered system designed to automatically route employee requests to the appropriate business domain and workflow. Instead of relying on manually reviewing every request, the system uses a local Large Language Model (Llama 3:8B) to understand the employee's request and identify the most relevant predefined domain and workflow.

The system follows a controlled routing approach where the AI can only choose from the domains and workflows defined in the system. The AI's classification is then validated by a deterministic Python decision layer before the request is routed. When the request is unclear or the model is not sufficiently confident, it is sent for human review rather than being routed based on a guess.

The application provides separate interfaces for employees and domain administrators. Employees can submit requests and track their progress, while administrators can review requests, request additional information, approve or reject requests, and manage them through their lifecycle until completion.

The project demonstrates how LLM-based natural language understanding can be integrated into an enterprise workflow while keeping the final routing process controlled, transparent, and human-supervised.
