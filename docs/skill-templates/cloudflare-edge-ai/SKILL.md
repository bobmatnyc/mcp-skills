---
name: Cloudflare Workers & Edge AI Development
skill_id: cloudflare-edge-ai
version: 1.0.0
description: Build ultra-low-latency edge computing applications with Cloudflare Workers, Workers AI for LLM inference, V8 isolates, Durable Objects, and serverless patterns deployed across 330+ data centers worldwide
category: Cloud & Serverless
tags:
  - cloudflare
  - edge-computing
  - serverless
  - workers
  - workers-ai
  - v8-isolates
  - durable-objects
  - edge-ai
  - low-latency
  - wrangler
author: mcp-skillset
license: MIT
created: 2025-11-25
last_updated: 2025-11-25
toolchain:
  - Cloudflare Workers
  - Wrangler CLI
  - Workers AI
  - TypeScript
frameworks:
  - Cloudflare Workers
  - Hono (lightweight framework)
  - Vectorize (vector DB)
related_skills:
  - fastapi-web-development
  - terraform-infrastructure
  - web3-blockchain
---

# Cloudflare Workers & Edge AI Development

## Overview

Master Cloudflare Workers - the fastest serverless platform with <1ms cold starts and Workers AI for running LLMs at the edge. Deploy across 330+ data centers globally for ultra-low-latency applications that run close to your users.

## When to Use This Skill

- Building globally distributed APIs with <50ms latency
- Running AI/LLM inference at the edge (Workers AI)
- Creating serverless backends without managing infrastructure
- Implementing edge middleware (auth, rate limiting, A/B testing)
- Building real-time collaborative applications (Durable Objects)
- Processing high-traffic workloads cost-effectively
- Deploying static sites with dynamic edge logic

## Core Principles

### 1. V8 Isolates (Not Containers)

**Workers run in V8 isolates - much faster than containers**

```typescript
// Basic Worker structure
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    // ✅ <1ms cold start (V8 isolate, not container!)
    // ✅ Runs in 330+ locations automatically
    // ✅ 0ms warm start (keeps isolate alive)

    return new Response("Hello from the edge!", {
      headers: { "Content-Type": "text/plain" }
    });
  }
};

// WRONG: Don't use Node.js APIs (not available)
// import fs from 'fs';  // ❌ No filesystem
// process.env.VAR;      // ❌ No process object

// CORRECT: Use Workers APIs
const value = env.MY_KV_NAMESPACE.get("key");  // ✅ KV storage
const response = await fetch("https://api.example.com");  // ✅ fetch API
```

**Key Differences from Node.js/Lambda**:
- ❌ No filesystem access
- ❌ No Node.js built-ins (fs, http, crypto from Node)
- ✅ Web Standard APIs (fetch, Request, Response, WebSockets)
- ✅ Sub-millisecond cold starts
- ✅ No VPC configuration needed

### 2. Workers AI - LLM Inference at the Edge

```typescript
// Run LLaMA 2, Mistral, or other models at the edge
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { prompt } = await request.json();

    // Text generation with LLaMA 2
    const response = await env.AI.run("@cf/meta/llama-2-7b-chat-int8", {
      messages: [
        { role: "system", content: "You are a helpful assistant" },
        { role: "user", content: prompt }
      ]
    });

    return Response.json(response);
  }
};

// Image generation
const image = await env.AI.run("@cf/stabilityai/stable-diffusion-xl-base-1.0", {
  prompt: "A futuristic city at sunset"
});

// Text embeddings (for vector search)
const embeddings = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
  text: "Hello, world!"
});

// Image classification
const result = await env.AI.run("@cf/microsoft/resnet-50", {
  image: imageBytes
});
```

**Workers AI Benefits**:
- 🚀 <50ms inference latency globally
- 💰 Pay only for inference time (no idle costs)
- 🌍 Runs in 330+ locations automatically
- 🔒 Data never leaves Cloudflare's network

### 3. KV Storage for Edge Data

```typescript
// wrangler.toml
# kv_namespaces = [
#   { binding = "MY_KV", id = "xxxxx", preview_id = "yyyyy" }
# ]

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const key = url.pathname.slice(1);

    // Read from KV (eventually consistent)
    const value = await env.MY_KV.get(key);

    if (value === null) {
      return new Response("Not found", { status: 404 });
    }

    // Write to KV
    await env.MY_KV.put("user:123", JSON.stringify({ name: "Alice" }), {
      expirationTtl: 3600,  // Expire in 1 hour
      metadata: { createdAt: Date.now() }
    });

    // List keys
    const list = await env.MY_KV.list({ prefix: "user:" });

    // Delete key
    await env.MY_KV.delete(key);

    return new Response(value);
  }
};
```

**KV Best Practices**:
- ✅ Use for read-heavy workloads (caching, config)
- ✅ Values up to 25 MB
- ✅ Eventually consistent (may take 60s to propagate)
- ❌ Not for transactional data or immediate consistency

### 4. Durable Objects for Stateful Logic

```typescript
// Durable Object - Single-instance, strongly consistent storage
export class RateLimiter {
  state: DurableObjectState;

  constructor(state: DurableObjectState, env: Env) {
    this.state = state;
  }

  async fetch(request: Request) {
    const count = (await this.state.storage.get("count")) || 0;
    const newCount = count + 1;

    if (newCount > 100) {
      return new Response("Rate limit exceeded", { status: 429 });
    }

    await this.state.storage.put("count", newCount);
    return new Response(`Request ${newCount}/100`);
  }
}

// Worker that uses Durable Object
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Get Durable Object instance (one per user)
    const id = env.RATE_LIMITER.idFromName("user:123");
    const stub = env.RATE_LIMITER.get(id);

    // Forward request to Durable Object
    return stub.fetch(request);
  }
};

// wrangler.toml
# [[durable_objects.bindings]]
# name = "RATE_LIMITER"
# class_name = "RateLimiter"
# script_name = "my-worker"
```

**Durable Objects Use Cases**:
- ✅ Real-time collaboration (Google Docs-style)
- ✅ WebSocket connections
- ✅ Distributed locks and coordination
- ✅ Game servers, chat rooms
- ✅ Strongly consistent counters

### 5. Vectorize for Edge Vector Search

```typescript
// Vector database at the edge
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { text } = await request.json();

    // Generate embedding with Workers AI
    const embedding = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: text
    });

    // Insert into vector database
    await env.VECTORIZE.insert([
      {
        id: "doc-1",
        values: embedding.data[0],
        metadata: { text: text }
      }
    ]);

    // Query similar vectors
    const results = await env.VECTORIZE.query(embedding.data[0], {
      topK: 5,
      returnMetadata: true
    });

    return Response.json(results);
  }
};

// wrangler.toml
# [[vectorize]]
# binding = "VECTORIZE"
# index_name = "my-index"
```

## Best Practices

### Request Routing & Middleware

```typescript
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { bearerAuth } from 'hono/bearer-auth';

const app = new Hono<{ Bindings: Env }>();

// CORS middleware
app.use('/*', cors({
  origin: ['https://example.com'],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE'],
}));

// Authentication middleware
app.use('/api/*', bearerAuth({ token: 'secret-token' }));

// Rate limiting
app.use('/api/*', async (c, next) => {
  const ip = c.req.header('cf-connecting-ip');
  const id = c.env.RATE_LIMITER.idFromName(ip);
  const limiter = c.env.RATE_LIMITER.get(id);

  const response = await limiter.fetch(c.req.raw);
  if (response.status === 429) {
    return c.text('Rate limit exceeded', 429);
  }

  await next();
});

// Routes
app.get('/api/users/:id', async (c) => {
  const userId = c.req.param('id');
  const user = await c.env.MY_KV.get(`user:${userId}`);
  return c.json(JSON.parse(user));
});

app.post('/api/chat', async (c) => {
  const { message } = await c.req.json();

  const response = await c.env.AI.run("@cf/meta/llama-2-7b-chat-int8", {
    messages: [{ role: "user", content: message }]
  });

  return c.json(response);
});

export default app;
```

### Caching Strategies

```typescript
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const cacheUrl = new URL(request.url);
    const cacheKey = new Request(cacheUrl.toString(), request);
    const cache = caches.default;

    // Check cache first
    let response = await cache.match(cacheKey);

    if (!response) {
      // Cache miss - fetch from origin
      response = await fetch(request);

      // Clone response to cache it
      response = new Response(response.body, response);
      response.headers.set("Cache-Control", "public, max-age=3600");

      // Don't await cache.put (let it run in background)
      ctx.waitUntil(cache.put(cacheKey, response.clone()));
    }

    return response;
  }
};
```

### Environment Variables & Secrets

```typescript
// wrangler.toml
# [vars]
# API_URL = "https://api.example.com"
#
# Run: wrangler secret put API_KEY
# (for sensitive values)

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const apiUrl = env.API_URL;       // From [vars]
    const apiKey = env.API_KEY;       // From secrets

    const response = await fetch(`${apiUrl}/data`, {
      headers: { "Authorization": `Bearer ${apiKey}` }
    });

    return response;
  }
};
```

## Common Patterns

### A/B Testing at the Edge

```typescript
export default {
  async fetch(request: Request): Promise<Response> {
    const cookie = request.headers.get('cookie') || '';
    const variant = cookie.includes('variant=b') ? 'B' : 'A';

    // Or use hash of IP for consistent assignment
    // const ip = request.headers.get('cf-connecting-ip');
    // const variant = hashIP(ip) % 2 === 0 ? 'A' : 'B';

    if (variant === 'B') {
      return fetch('https://variant-b.example.com');
    }

    return fetch('https://variant-a.example.com');
  }
};
```

### Geolocation-Based Routing

```typescript
export default {
  async fetch(request: Request): Promise<Response> {
    const country = request.cf?.country;

    if (country === 'US') {
      return fetch('https://us.api.example.com');
    } else if (country === 'EU') {
      return fetch('https://eu.api.example.com');
    }

    return fetch('https://global.api.example.com');
  }
};
```

## Anti-Patterns

### ❌ DON'T: Block the response

```typescript
// BAD: Slow, synchronous loop
export default {
  async fetch(request: Request): Promise<Response> {
    for (let i = 0; i < 1000000; i++) {
      // Blocks isolate!
    }
    return new Response("Done");
  }
};

// GOOD: Use ctx.waitUntil for background work
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    ctx.waitUntil(
      (async () => {
        // Background work (logging, analytics)
        await env.MY_KV.put("last-request", Date.now());
      })()
    );

    return new Response("Done");
  }
};
```

### ❌ DON'T: Use Workers for long-running tasks

```
Workers CPU limit: 10ms (free), 50ms (paid), 30s (unbound)

✅ Good for: API requests, edge logic, AI inference
❌ Bad for: Video encoding, large file processing, long ML training
```

## Testing & Development

```bash
# Install Wrangler CLI
npm install -g wrangler

# Create new project
wrangler init my-worker

# Local development (with Workers AI, KV, DO)
wrangler dev

# Deploy to production
wrangler deploy

# Tail logs
wrangler tail

# Run tests with Vitest
npm test
```

## Related Skills

- **fastapi-web-development**: Compare serverless vs traditional APIs
- **terraform-infrastructure**: Deploy Workers with Terraform
- **web3-blockchain**: Build Web3 apps on Cloudflare

## Additional Resources

- Workers Documentation: https://developers.cloudflare.com/workers
- Workers AI Models: https://developers.cloudflare.com/workers-ai/models
- Durable Objects: https://developers.cloudflare.com/durable-objects
- Examples: https://github.com/cloudflare/workers-sdk/tree/main/templates

## Example Questions

- "How do I run LLaMA 2 at the edge with Workers AI?"
- "Show me how to implement rate limiting with Durable Objects"
- "What's the difference between KV and Durable Objects?"
- "How do I cache API responses at the edge?"
- "Write a Worker that does geolocation-based routing"
