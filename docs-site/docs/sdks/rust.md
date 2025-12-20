---
sidebar_position: 5
---

# Rust SDK

The official Rust SDK for QWED.

## Installation

```toml
[dependencies]
qwed = "1.0"
tokio = { version = "1.0", features = ["rt-multi-thread", "macros"] }
```

## Quick Start

```rust
use qwed::QWEDClient;

#[tokio::main]
async fn main() -> Result<(), qwed::Error> {
    let client = QWEDClient::new("qwed_your_key");
    
    let result = client.verify("Is 2+2=4?").await?;
    println!("Verified: {}", result.verified);  // true
    println!("Status: {:?}", result.status);    // Verified
    
    Ok(())
}
```

## Methods

### verify

```rust
let result = client.verify("2+2=4").await?;
```

### verify_math

```rust
let result = client.verify_math("x**2 + 2*x + 1 = (x+1)**2").await?;
println!("{}", result.verified);  // true
```

### verify_logic

```rust
let result = client.verify_logic("(AND (GT x 5) (LT y 10))").await?;
println!("{:?}", result.model);  // Some({"x": 6, "y": 9})
```

### verify_code

```rust
let result = client.verify_code(code, "python").await?;
for vuln in &result.vulnerabilities {
    println!("{}: {}", vuln.severity, vuln.message);
}
```

### verify_sql

```rust
let result = client.verify_sql(query, schema, "postgresql").await?;
```

### verify_batch

```rust
let items = vec![
    BatchItem { query: "2+2=4".into(), r#type: Some(VerificationType::Math) },
    BatchItem { query: "3*3=9".into(), r#type: Some(VerificationType::Math) },
];
let results = client.verify_batch(items).await?;
println!("{:.1}%", results.summary.unwrap().success_rate);
```

## Types

```rust
pub enum VerificationStatus {
    Verified,
    Failed,
    Corrected,
    Blocked,
    Error,
}

pub struct VerificationResponse {
    pub status: VerificationStatus,
    pub verified: bool,
    pub engine: String,
    pub result: Option<serde_json::Value>,
}
```

## Error Handling

```rust
match client.verify("test").await {
    Ok(result) => println!("Verified: {}", result.verified),
    Err(qwed::Error::Auth) => eprintln!("Invalid API key"),
    Err(qwed::Error::RateLimit) => eprintln!("Rate limit exceeded"),
    Err(e) => eprintln!("Error: {}", e),
}
```
