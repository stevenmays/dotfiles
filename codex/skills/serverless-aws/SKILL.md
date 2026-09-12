---
name: serverless-aws
description: Design or change AWS Lambda handlers, SQS consumers, and DynamoDB-backed workflows when serverless behavior is central to the task.
---

# Serverless AWS

Follow the application's existing event contracts, authentication boundaries, observability, and deployment configuration. Keep handlers focused on translating events and coordinating domain logic.

- Reuse SDK clients across invocations where appropriate. Cache configuration only when its freshness requirements permit it.
- Validate external event data before using it. Avoid logging complete request headers, bodies, credentials, or sensitive payloads by default.
- Read the actual SQS batch and retry configuration. Handle all delivered records; do not assume a batch contains one record. Make retry and partial-failure behavior explicit.
- Treat duplicate delivery as part of the workflow. A process-local map is not durable deduplication across invocations or workers. Use durable state and atomic operations when the operation requires idempotency.
- Keep related state transitions atomic where possible. Bound retries and preserve enough context to diagnose a failed external call without exposing secrets.

Consult current AWS documentation for SDK syntax, event-source semantics, service limits, and deployment settings needed by the change. Use the project's local tests and disposable fixtures when available. Check before executing commands that would mutate live AWS resources.
