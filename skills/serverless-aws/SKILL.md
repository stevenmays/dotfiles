---
name: serverless-aws
description: Patterns for AWS Lambda, DynamoDB, SQS, and Secrets Manager. Use when working on serverless AWS projects.
---

# Serverless AWS Skill

Patterns for AWS Lambda, DynamoDB, SQS, and Secrets Manager.

## When to Use

Apply when working on serverless AWS projects using Lambda functions.

## Lambda Handler Structure

Log the request ID and the error's stack, never `event.headers` or `event.body`: both carry tokens and personal data. Don't log the error object itself: Node prints its own properties too, and many clients keep request data there. Keep request and response data out of error messages, because the message is the first line of the stack. API Gateway sets `event.body` to `null` for a request without a body. Guard it before `JSON.parse`, and return 400 for malformed input instead of throwing.

```typescript
import type { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';

export async function handle(event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> {
    try {
        return await handleRequest(event);
    } catch (error) {
        console.error('Request failed', {
            requestId: event.requestContext.requestId,
            error: error instanceof Error ? error.stack : 'non-Error value thrown',
        });
        return { statusCode: 500, body: JSON.stringify({ message: 'Internal error' }) };
    }
}

async function handleRequest(event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> {
    if (!(await isAuthorizedWidgetClient(event))) return { statusCode: 401, body: '' };
    if (!event.body) return badRequest('Missing request body');

    let input: unknown;
    try {
        input = JSON.parse(event.body);
    } catch {
        return badRequest('Request body is not valid JSON');
    }
    if (!isWidgetOrder(input)) return badRequest('Invalid widget order');
    return createWidgetOrder(input);
}

function badRequest(message: string): APIGatewayProxyResult {
    return { statusCode: 400, body: JSON.stringify({ message }) };
}
```

## Cold Start Optimization

Create SDK clients at module scope, so every invocation in an execution environment reuses them. Cache configuration the same way only when it can stay stale until Lambda recycles the environment.

```typescript
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';

// The Lambda runtime sets AWS_REGION, so the client needs no region.
const dynamo = new DynamoDBClient({});

let widgetSettings: WidgetSettings | undefined;

export async function handle(event: WidgetEvent) {
    widgetSettings ??= await loadWidgetSettings();
    return handleWidgetEvent(event, widgetSettings);
}
```

## SQS Processing

Process every record and return the failed ones in `batchItemFailures`, so SQS retries only those records. The response takes effect only when the event source mapping sets `FunctionResponseTypes` to `ReportBatchItemFailures`. Without that setting, Lambda ignores the response and deletes the whole batch when the handler returns. Throw for an unknown message type: SQS retries the record, then moves it to the dead-letter queue after the redrive policy's `maxReceiveCount`. Give the queue a redrive policy with a dead-letter queue: without one, SQS retries the record until the retention period ends, then deletes it. This handler is for a standard queue. For a FIFO queue, stop at the first failure and report that record and every record after it, so later messages in a group don't run ahead of a retry.

```typescript
import type { SQSBatchItemFailure, SQSBatchResponse, SQSEvent, SQSRecord } from 'aws-lambda';

export async function handle(event: SQSEvent): Promise<SQSBatchResponse> {
    const batchItemFailures: SQSBatchItemFailure[] = [];
    for (const record of event.Records) {
        try {
            await handleRecord(record);
        } catch (error) {
            console.error('Record failed', {
                messageId: record.messageId,
                error: error instanceof Error ? error.stack : 'non-Error value thrown',
            });
            batchItemFailures.push({ itemIdentifier: record.messageId });
        }
    }
    return { batchItemFailures };
}

async function handleRecord(record: SQSRecord) {
    const message = parseMessageBody(record.body);
    const type = record.messageAttributes.type?.stringValue;
    switch (type) {
        case 'WIDGET_SHIPPED': return handleWidgetShipped(message);
        case 'WIDGET_RETURNED': return handleWidgetReturned(message);
        default: throw new Error('Unknown message type');
    }
}

// JSON.parse errors quote part of the input, and the input must not reach the log.
function parseMessageBody(body: string): unknown {
    try {
        return JSON.parse(body);
    } catch {
        throw new Error('Message body is not valid JSON');
    }
}
```

## External API Calls

Put only the status code in the error, because the response body can echo request data. For the same reason, replace a JSON parse error with a fixed message: its text quotes part of the body. The caller's handler logs the error once, with its request ID or message ID. Lambda's default function timeout is 3 seconds. Keep the `fetch` timeout below it, and raise the function timeout when one invocation makes several calls, such as one per SQS record.

```typescript
class PartnerApiError extends Error {
    status: number;

    constructor(status: number) {
        super(`Partner API returned ${status}`);
        this.status = status;
    }
}

export async function postToPartnerApi(path: string, payload: unknown): Promise<unknown> {
    const { baseUrl, apiKey } = await loadPartnerApiSettings();
    const response = await fetch(`${baseUrl}${path}`, {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(2_000),
    });
    if (!response.ok) {
        // Release the connection without reading a body that can echo request data.
        await response.body?.cancel();
        throw new PartnerApiError(response.status);
    }
    try {
        return await response.json();
    } catch (error) {
        if (error instanceof SyntaxError) throw new Error('Partner API returned invalid JSON');
        throw error;
    }
}
```

## Deduplication

SQS can deliver a message more than once, and Lambda runs many execution environments at once. A module-scope `Map` sees only its own environment and empties on every cold start. Make the duplicate check and the effect one conditional write, so they succeed or fail together. The table's partition key is `eventId`, so the condition fails only when that event is already recorded.

```typescript
import { ConditionalCheckFailedException, DynamoDBClient, PutItemCommand } from '@aws-sdk/client-dynamodb';

const dynamo = new DynamoDBClient({});
const SHIPMENTS_TABLE = process.env.SHIPMENTS_TABLE_NAME;

export async function recordShipmentOnce(eventId: string, widgetId: string): Promise<'recorded' | 'duplicate'> {
    try {
        await dynamo.send(new PutItemCommand({
            TableName: SHIPMENTS_TABLE,
            Item: {
                eventId: { S: eventId },
                widgetId: { S: widgetId },
            },
            ConditionExpression: 'attribute_not_exists(eventId)',
        }));
        return 'recorded';
    } catch (error) {
        if (error instanceof ConditionalCheckFailedException) return 'duplicate';
        throw error;
    }
}
```

Don't write a claim marker and then call another service. If the function times out between the two, the retry finds the marker and skips the event. When the other service accepts an idempotency key, pass the event ID as that key. When it accepts none, read the marker first with a strongly consistent `GetItem` (`ConsistentRead: true`), and skip the event when the marker exists. Otherwise call the service, then write the marker. A crash between the call and the write, or 2 concurrent deliveries, can still repeat the call: no marker or lease makes such a call happen exactly once. When a repeat is unacceptable, use a service that accepts an idempotency key, or reconcile against the service's own records. When the effect spans several DynamoDB items, write the marker and the items in one `TransactWriteItems` call. A failed condition there throws `TransactionCanceledException`, which also covers throttling and transaction conflicts. Return `'duplicate'` only when `CancellationReasons` shows `ConditionalCheckFailed` for the marker's item, and rethrow every other cancellation.
