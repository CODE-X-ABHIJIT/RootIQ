# RootIQ

**RootIQ** is an open-source Kubernetes root cause analysis (RCA) and repair-assistance CLI that helps engineers investigate cluster issues, understand their causes, plan repairs, validate outcomes, and generate incident reports.

RootIQ provides four main commands:

* **Inspect** — Collect Kubernetes resource information and identify potential issues.
* **Repair** — Analyze detected issues, prepare repair actions, and request user approval before executing supported repairs.
* **Validate** — Check cluster health and assess the results of troubleshooting or repair actions.
* **Report** — Generate structured reports to support incident review and troubleshooting.

RootIQ is designed to make Kubernetes incident investigation more structured and repeatable. Repairs are not performed autonomously: users review and approve proposed actions before execution.

CLI  : pip install rootiq

LINK : https://pypi.org/project/rootiq/0.1.0/
---

## 📖 Overview

RootIQ streamlines Kubernetes incident investigation by collecting cluster data, analyzing issues with a rule-based engine, preparing repair plans for user review and approval, validating outcomes, and generating structured incident reports—all through a single command-line interface.

---

## ✨ Features

* 🔍 Kubernetes resource inspection and issue detection
* 🧠 Rule-based root cause analysis (RCA)
* 🛠️ Planned repairs with user approval before execution
* ✅ Post-repair validation
* 📄 Structured incident reporting
* 📦 Incident lifecycle and persistent incident storage
* ☸️ Kubernetes-native resource collectors

---

## 🏗️ Project Structure

```text
RootIQ/
│
├── rootiq/
│   ├── cli/
│   ├── collectors/
│   ├── analyzers/
│   ├── rule_engine/
│   ├── repair_engine/
│   ├── validators/
│   ├── reports/
│   ├── incident/
│   ├── kubernetes/
│   ├── config/
│   └── utils/
│
├── rules/
├── templates/
├── docs/
├── tests/
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 🧩 Incident Lifecycle

```text
NEW
   │
   ▼
INSPECTING
   │
   ▼
DIAGNOSED
   │
   ▼
REPAIRING
   │
   ▼
VALIDATED
   │
   ▼
RESOLVED
   │
   ▼
CLOSED
```

---

## ⚙️ Planned Workflow

```text
Inspect Cluster
        │
        ▼
Collect Kubernetes Resources
        │
        ▼
Analyze Cluster State
        │
        ▼
Identify Root Cause
        │
        ▼
Generate Incident
        │
        ▼
Execute Repair
        │
        ▼
Validate Recovery
        │
        ▼
Generate RCA Report
```

---

## 📋 CLI Commands

```bash
rootiq inspect
```

Performs a comprehensive inspection of the Kubernetes cluster and creates an incident when issues are detected.

```bash
rootiq repair
```

Executes automated remediation based on the identified root cause.

```bash
rootiq validate
```

Verifies that the repair has successfully resolved the issue.

```bash
rootiq report
```

Generates a detailed incident report containing diagnostics, root cause analysis, repair actions, validation results, and recommendations.

---

## 🛠️ Technology Stack

* Python 3
* Kubernetes Python Client
* YAML
* JSON
* Docker
* GitHub Actions
* Linux
* AWS (EKS)
* Kubernetes

---

## 📦 Core Components

### Collectors

Collect cluster resources such as Pods, Deployments, ReplicaSets, StatefulSets, DaemonSets, Services, PVCs, PVs, Nodes, Events, ConfigMaps, Secrets, HPAs, Jobs, CronJobs, and other Kubernetes objects.

### Rule Engine

Evaluates collected data against configurable diagnostic rules to identify the most probable root cause.

### Analyzer

Correlates events, logs, metrics, and Kubernetes resource states to produce intelligent diagnostics.

### Repair Engine

Executes automated recovery actions while maintaining operational safety and traceability.

### Validator

Confirms that the cluster has returned to a healthy state after remediation.

### Reporting

Generates structured incident reports with RCA, repair history, validation outcomes, and recommendations.

---

## 🎯 Objectives

* Reduce Mean Time To Detect (MTTD)
* Reduce Mean Time To Resolve (MTTR)
* Standardize Kubernetes incident handling
* Automate repetitive operational tasks
* Improve production reliability
* Simplify Kubernetes troubleshooting

---

## 🚀 Future Enhancements

* Multi-cluster management
* FastAPI REST API
* Web dashboard
* Slack and Microsoft Teams integration
* Email notifications
* Prometheus integration
* Grafana integration
* AI-assisted RCA
* Helm chart deployment
* Kubernetes Operator support
* Multi-cloud support (EKS, AKS, GKE, OpenShift)

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome. Feel free to fork the repository, create a feature branch, and submit a pull request.

---

## 📄 License

This project is licensed under the Apache License 2.0 .

---

## 👨‍💻 Author

**Abhijit Sahu**

Cloud | DevOps | Kubernetes | AWS | Python
