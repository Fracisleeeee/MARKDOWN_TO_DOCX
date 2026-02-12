---
title: Sample Technical Report
author: Build System
date: 2026-02-12
template: tech
toc: true
mermaid: true
page_break_h1: true
---

# Overview

This is a sample document for the Markdown to DOCX engine.

## Architecture

```mermaid
flowchart TD
  A[Markdown] --> B[Pandoc]
  B --> C[DOCX]
```

## Data Table

| Component | Status | Notes |
| --- | --- | --- |
| Parser | Done | Reads front matter and body |
| Mermaid | Done | Renders SVG and caches by hash |
| Tables | MVP | Supports standard markdown tables |

# Next Steps

This section should start on a new page when pagination is enabled.
