# AI Procurement Copilot v1.2 — Visual Design System

## Purpose

This design system standardizes public portfolio assets without changing application logic. It is intended for README visuals, recruiter material, LinkedIn assets and controlled demonstration content.

## Core palette

| Role | Hex | Usage |
|---|---|---|
| Primary background | `#F4F7FB` | Page and visual canvas |
| Surface | `#FFFFFF` | Cards and panels |
| Primary text | `#132238` | Headings and body copy |
| Secondary text | `#5B6B7F` | Supporting copy and captions |
| Main accent | `#1F5EFF` | Navigation, callouts and emphasis |
| Enterprise navy | `#0B1F3A` | Covers, headers and title bands |
| Success | `#13795B` | Passed or eligible status |
| Warning | `#A15C00` | Review or conditional status |
| Failure / blocked | `#B42318` | Blocked status and explicit exclusions |
| Border | `#D8E0EA` | Card and section separation |

Validation status must never rely on colour alone. Every status requires a text label such as **PASS**, **WARNING**, **BLOCKED**, **Eligible** or **Human review required**.

## Typography

Use Arial or another widely available sans-serif fallback.

- Hero title: 44–52 px, bold
- Major section heading: 28–34 px, bold
- Card heading: 20–24 px, bold
- Body text: 18–20 px
- Supporting text: 14–16 px

Avoid condensed fonts, decorative scripts and dense all-capital paragraphs.

## Spacing and components

- Outer page margin: 56–72 px on 1600 × 900 assets
- Card gap: 24–32 px
- Card padding: 28–36 px
- Border radius: 18–28 px
- Use one principal message per card
- Use no more than four status pills in a single row
- Keep callouts numbered, short and directional

## Chart and diagram rules

- Use flat, restrained fills
- Do not use decorative gradients
- Prefer direct labels to legends
- Show validation gates explicitly
- Keep arrows unidirectional
- Separate business-readable outputs from machine-readable audit data
- Always end decision-flow visuals with human procurement review

## Screenshot annotation rules

- Use numbered blue circles
- Use thin connector lines
- Keep callout text below eight words where possible
- Do not obscure values or navigation labels
- Do not annotate sensitive, confidential or live organizational data

## Public-asset rules

- Use only synthetic, sanitized or generic information
- Do not present illustrative values as realized savings
- Do not imply live ERP connectivity
- Do not show the removed Interview Guide
- Do not claim production deployment, enterprise scale or autonomous awards
- Label mockups and conceptual visuals as illustrative where they are not direct hosted captures

## Asset format

The Build Group C assets are maintained as SVG files so text remains searchable, the files remain reviewable in Git and the visuals can be exported to PNG later without changing source content.
