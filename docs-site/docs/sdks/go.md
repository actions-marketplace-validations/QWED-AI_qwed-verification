---
sidebar_position: 4
---

# Go SDK

The official Go SDK for QWED.

## Installation

```bash
go get github.com/qwed-ai/qwed-go
```

## Quick Start

```go
package main

import (
    "context"
    "fmt"
    "github.com/qwed-ai/qwed-go"
)

func main() {
    client := qwed.NewClient("qwed_your_key")
    
    result, err := client.Verify(context.Background(), "Is 2+2=4?")
    if err != nil {
        panic(err)
    }
    
    fmt.Println(result.Verified)  // true
    fmt.Println(result.Status)    // "VERIFIED"
}
```

## Methods

### Verify

```go
result, err := client.Verify(ctx, "2+2=4")
```

### VerifyMath

```go
result, err := client.VerifyMath(ctx, "x**2 + 2*x + 1 = (x+1)**2")
fmt.Println(result.Verified)  // true
```

### VerifyLogic

```go
result, err := client.VerifyLogic(ctx, "(AND (GT x 5) (LT y 10))")
fmt.Println(result.Model)  // map[x:6 y:9]
```

### VerifyCode

```go
result, err := client.VerifyCode(ctx, code, "python")
for _, vuln := range result.Vulnerabilities {
    fmt.Printf("%s: %s\n", vuln.Severity, vuln.Message)
}
```

### VerifySQL

```go
result, err := client.VerifySQL(ctx, query, schema)
```

### VerifyBatch

```go
items := []qwed.BatchItem{
    {Query: "2+2=4", Type: qwed.TypeMath},
    {Query: "3*3=9", Type: qwed.TypeMath},
}
results, err := client.VerifyBatch(ctx, items)
fmt.Println(results.Summary.SuccessRate)
```

## Types

```go
type VerificationResult struct {
    Status          string
    Verified        bool
    Engine          string
    Result          map[string]interface{}
    Vulnerabilities []Vulnerability
}
```

## Error Handling

```go
result, err := client.Verify(ctx, "test")
if err != nil {
    var qwedErr *qwed.Error
    if errors.As(err, &qwedErr) {
        fmt.Println(qwedErr.Code)
        fmt.Println(qwedErr.Message)
    }
}
```
