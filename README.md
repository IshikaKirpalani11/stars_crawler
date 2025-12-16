# GitHub Stars Crawler

A production-style GitHub crawler that fetches star counts for GitHub repositories using GitHub’s GraphQL API and stores them efficiently in PostgreSQL.

This project is designed following clean architecture principles, with a strong focus on scalability, immutability, and efficient database updates.

---

## 🚀 Features

- Fetches up to **100,000 GitHub repositories**
- Respects GitHub API rate limits
- Efficient **UPSERT-based** database updates
- PostgreSQL-backed storage
- Fully automated **GitHub Actions pipeline**
- Daily scheduled crawling
- Artifact export of database dump

---

## 🏗 Architecture Overview

app/
├── domain/ # Core domain models (future expansion)
├── infrastructure/
│ ├── github/ # GitHub API integration (anti-corruption layer)
│ └── db/ # Database logic
├── services/ # Application services
└── config.py
scripts/
└── crawl_stars.py # Entry point


### Clean Architecture Principles
- **Separation of concerns** between API, persistence, and orchestration
- **Anti-corruption layer** between GitHub API and internal models
- Minimal shared mutable state
- Database is treated as an append/update-only system

---

## 🧪 Database Schema

```sql
CREATE TABLE github_repos (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    owner TEXT NOT NULL,
    stars INT NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

⚙ GitHub Actions Pipeline

The crawler runs inside a GitHub Actions workflow that:

Starts a PostgreSQL service container

Installs Python dependencies

Creates the database schema

Crawls GitHub repositories via GraphQL

Upserts star counts efficiently

Dumps the database as an artifact

Triggers

Manual (workflow_dispatch)

Push to main

Daily scheduled crawl via cron

This ensures continuous data freshness without manual intervention.

🔄 Daily Crawling Strategy

The crawler runs daily using a scheduled GitHub Actions workflow

Repository records are upserted, not reinserted

Only mutable fields (stars, updated_at) are updated

Immutable identifiers (id, name, owner) remain unchanged

This minimizes database writes and allows efficient continuous updates.

📈 Scaling from 100K to 500M Repositories

To scale this system to hundreds of millions of repositories, the following changes would be required:

Crawling

Distributed workers (Kafka / PubSub)

Cursor-based partitioning

Adaptive rate-limit scheduling

Incremental crawling using checkpoints

Storage

Table partitioning or sharding

Hot/cold data separation

Migration to distributed SQL databases if required

API Efficiency

GraphQL query batching

Exponential backoff & retries

Priority-based crawling for active repositories

🧬 Schema Evolution for Future Metadata

To support additional GitHub metadata such as issues, pull requests, comments, reviews, and CI checks:

Introduce separate tables per entity

Use append-only models for comments and events

Store aggregated counts at the parent level

Example:

UPDATE pull_requests
SET comment_count = 20, updated_at = NOW()
WHERE id = 'PR_123';


This ensures:

Minimal rows affected

Efficient incremental updates

No rewriting of historical data

🧠 Design Summary

This project demonstrates:

Clean architecture with clear boundaries

Efficient relational modeling

Scalable ingestion design

CI-driven automation

Production-grade data update strategies