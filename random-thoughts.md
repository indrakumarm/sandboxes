# Sandboxed ML Deployment MVP

A minimal, opinionated proof-of-concept for **secure and reproducible ML model deployment** using Kubernetes native primitives.

This project demonstrates how ML inference services can be deployed in **isolated sandboxes** with controlled resource usage, network access, and safe rollout mechanisms.

---

## 🎯 Goal

To build a **small but realistic sandboxing platform** that answers:

> How can we safely deploy ML models as services without allowing them to:
> - Exhaust cluster resources
> - Access other workloads
> - Affect platform stability?

This MVP focuses on **platform fundamentals**, not ML model accuracy.

---

## 🧱 Design Principles

- **Kubernetes-native** (no custom operators)
- **Strong isolation by default**
- **Minimal surface area**
- **Reproducible deployments**
- **Interview-demo friendly**

---

## 🏗️ Architecture Overview

