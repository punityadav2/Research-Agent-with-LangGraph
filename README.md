# Autonomous Research Agent with LangGraph, Groq, and Streamlit

This repository contains the complete source code for an **autonomous AI research agent**. The agent takes a user-defined topic, performs web searches to gather information, evaluates and summarizes relevant sources, and compiles the findings into a comprehensive report.

The project is built using a modern AI stack, showcasing a stateful, cyclic architecture that enables complex, multi-step reasoning and execution, all presented through an interactive web interface.



---

## Core Technologies

- **Orchestration:** `LangGraph` – Build stateful, multi-actor applications with cycles, enabling complex agentic behaviors.  
- **LLM:** `Groq` – High-speed inference using a Language Processing Unit (LPU) for fast and responsive AI reasoning.  
- **Web Interface:** `Streamlit` – Interactive and user-friendly chat-based web application built entirely in Python.  
- **Search Tool:** `Tavily AI` – AI-optimized search engine to gather accurate and relevant information from the web.  
- **Core Framework:** `LangChain` – Provides foundational components, tools, and integrations.  
  

---

## Key Features

- **Stateful, Cyclic Architecture:**  
  Uses LangGraph loops to iteratively search, evaluate, and decide whether to continue researching or compile findings, mimicking a human research process.  

- **High-Performance LLM:**  
  Leverages Groq LPU for reasoning and content generation at extremely high speeds for a seamless user experience.  

- **Fault Tolerance and Persistence:**  
  Saves the agent’s state at every step using `SqliteSaver` checkpointer, allowing long-running tasks to resume from the exact point of failure.  

- **Interactive Web UI:**  
  Streamlit-based chat interface lets users input topics, monitor progress in real-time, and receive the final report directly in the app.  

- **Deep Observability with LangSmith:**  
  Provides detailed traces of every agent step for debugging and understanding complex behavior.  

---
