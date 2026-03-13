# Multi-Agent Design Patterns

Research from Brave Search - 2026-03-12

## Core Patterns

Based on research from Google, Microsoft, LangChain, and other sources:

### 1. Sequential Pattern
Agents process tasks in a linear pipeline. Each agent's output becomes the input for the next.
- **Use case**: Well-defined workflows with clear dependencies
- **Our implementation**: Design → Code → QA pipeline ✅

### 2. Parallel Pattern
Multiple agents work simultaneously on independent tasks.
- **Use case**: When tasks are independent and can be done concurrently

### 3. Loop Pattern
Iterative workflow where agents can revisit previous steps.
- **Use case**: Refinement cycles, reviews

### 4. Orchestrator-Worker
A central coordinator (Hermes) delegates tasks to specialized agents.
- **Use case**: Our current setup! Hermes coordinates Hefesto, Athena, Apollo

### 5. Hierarchical Supervision
Supervising agents monitor and guide sub-agents.
- **Use case**: Quality control, escalation

### 6. Router Pattern
LLM decides which agent should handle a request.
- **Use case**: Classification, routing to specialists

### 7. Swarm Pattern
Agents dynamically pass control to each other based on expertise.
- **Use case**: Dynamic task distribution

## Our Architecture

We are using **Orchestrator-Worker** pattern:
- **Hermes** (Coordinator) → Routes work
- **Hefesto** (Coder) → Implementation
- **Athena** (Designer) → Specifications
- **Apollo** (QA) → Validation

## References

- Microsoft Azure: AI Agent Orchestration Patterns
- Google ADK: Multi-agent systems
- LangChain: Multi-agent architectures
- Confluent: Event-driven multi-agent patterns
- DeepLearning.AI: Agentic Design Patterns Part 5
- MongoDB: 7 Practical Design Patterns for Agentic Systems

## Future Improvements

Consider adding:
- Parallel execution for independent tasks
- Loop patterns for review cycles
- Router for automatic task classification
