---
sidebar_position: 3
---

# TypeScript SDK

The official TypeScript/JavaScript SDK for QWED.

## Installation

```bash
npm install @qwed-ai/sdk
# or
yarn add @qwed-ai/sdk
# or
pnpm add @qwed-ai/sdk
```

## Quick Start

```typescript
import { QWEDClient } from '@qwed-ai/sdk';

const client = new QWEDClient({ apiKey: 'qwed_your_key' });

const result = await client.verify('Is 2+2=4?');
console.log(result.verified);  // true
console.log(result.status);    // "VERIFIED"
```

## Configuration

```typescript
const client = new QWEDClient({
  apiKey: 'qwed_...',
  baseUrl: 'http://localhost:8000',  // Optional
  timeout: 30000,  // Optional, default 30s
});
```

## Methods

### verify(query)

```typescript
const result = await client.verify('What is 15% of 200?');
```

### verifyMath(expression)

```typescript
const result = await client.verifyMath('x**2 + 2*x + 1 = (x+1)**2');
console.log(result.verified);  // true
```

### verifyLogic(query)

```typescript
const result = await client.verifyLogic('(AND (GT x 5) (LT y 10))');
console.log(result.model);  // { x: 6, y: 9 }
```

### verifyCode(code, language)

```typescript
const result = await client.verifyCode(code, 'python');
for (const vuln of result.vulnerabilities) {
  console.log(`${vuln.severity}: ${vuln.message}`);
}
```

### verifySQL(query, schema)

```typescript
const result = await client.verifySQL(
  'SELECT * FROM users WHERE id = 1',
  'CREATE TABLE users (id INT, name TEXT)'
);
```

### verifyBatch(items)

```typescript
const results = await client.verifyBatch([
  { query: '2+2=4', type: 'math' },
  { query: '3*3=9', type: 'math' },
]);
console.log(results.summary.successRate);
```

## TypeScript Types

```typescript
import {
  VerificationResult,
  VerificationType,
  VerificationStatus,
  BatchResult,
} from '@qwed-ai/sdk';
```

## Error Handling

```typescript
import { QWEDError } from '@qwed-ai/sdk';

try {
  const result = await client.verify('test');
} catch (error) {
  if (error instanceof QWEDError) {
    console.log(error.code);    // "QWED-001"
    console.log(error.message); // "Verification failed"
  }
}
```
