# DEPLOYMENT PLAN (BETA)

## Inference and Dashboard Prototypes 

Jupyter notebooks were run either locally or with Google Colab Pro to leverage A100 GPUs. A prototype version of the dashboard was created using [Streamlit](https://zero-emission-vehicle-data-analyzer-csb.streamlit.app/) to visualize key insights from EV charging session data. This dashboard will be incorporated into a larger AI Interface project using Next.js, Django and MySQL and will be described in [this repository](https://github.com/elmunoz42/ai-interface).

## Current Project Phase

We are currently in a **planning phase with the County of Santa Barbara's IT department** to determine the cloud resources that need to be provisioned for production workloads. The subsequent sections of this document outline the architecture that is being planned for secure, scalable deployment on AWS. 

---

## EV Charging Data Processing System on Amazon SageMaker

This document describes the secure and scalable AWS architecture used to process EV charging session data using Amazon SageMaker Studio notebooks. The architecture is designed with network isolation, controlled access, and VPC endpoints to restrict data movement while enabling necessary AWS service communication.

---

## 🧱 Architecture Components

<img width="857" height="371" alt="image" src="https://github.com/user-attachments/assets/1c751de6-9fb2-41a2-a25c-7da30a59b18e" />


### 1. **Amazon SageMaker Studio**
- Provides an integrated development environment for data scientists.
- Used for ingesting and processing EV charging session data.
- Hosted in a secure Amazon Virtual Private Cloud (VPC).

### 2. **Amazon VPC**
- A logically isolated network environment hosting SageMaker Studio and related resources.
- Contains:
  - **Private Subnet**: Hosts SageMaker notebooks and EFS (optional).
  - **Public Subnet**: Hosts a **NAT Gateway** for outbound internet access (egress-only).

### 3. **Elastic Network Interfaces (ENIs)**
- Automatically created when SageMaker Studio is launched.
- Enable secure communication between SageMaker and other AWS services.
- Associated with a **Security Group** that controls traffic.

### 4. **Amazon EFS (Optional)**
- Used for persistent file storage across notebook sessions.
- Attached to the notebook instances within the private subnet.

---

## 🔐 Security Controls

### ✅ Security Groups
- Act as virtual firewalls for ENIs.
- Limit inbound/outbound traffic to/from SageMaker notebooks.
- Example rule: Allow only port `8888` from trusted IPs for Jupyter notebook access.

### ✅ VPC Endpoints
- Provide **private connectivity** to supported AWS services without traversing the internet.
- Configured with **endpoint policies** for fine-grained access control.
- Used to access:
  - Amazon S3
  - Amazon CloudWatch Logs
  - SageMaker Runtime
  - SageMaker API

### ✅ NAT Gateway
- Located in the public subnet.
- Allows resources in the private subnet to **egress to the internet** securely (e.g., for downloading packages).
- Prevents external systems from initiating connections.

---

## 🗂 VPC Endpoints and Policies

| Service              | Endpoint Type | Purpose                                  |
|----------------------|----------------|------------------------------------------|
| Amazon S3            | Gateway        | Store and retrieve EV session data       |
| CloudWatch Logs      | Interface      | Send logs for monitoring/troubleshooting |
| SageMaker Runtime    | Interface      | Run model inference                      |
| SageMaker API        | Interface      | Interact with SageMaker control plane    |

Each endpoint has a **policy** attached to define:
- Which IAM users/roles can access it
- What actions are allowed
- Which resources can be accessed

---

## 🔄 Data Flow

1. **Data Scientist** accesses **SageMaker Studio** via a browser.
2. Notebooks are launched inside the **VPC private subnet**.
3. EV charging session data is pulled from:
   - Amazon S3 (historical data)
   - Streaming sources (if applicable, not shown)
4. Notebooks process and analyze data.
5. Processed outputs/logs are stored back in Amazon S3 or logged in CloudWatch.

---

## 🔒 Best Practices

- **Isolate ML resources**: All processing is performed within a private subnet.
- **Restrict internet access**: No direct internet exposure; only controlled egress via NAT Gateway.
- **Use VPC endpoint policies** to limit access to critical AWS services.
- **Security groups and NACLs** enforce granular traffic control.
- **No inbound internet access**: Ensures strong network-level isolation.

---

## 📌 Summary

This architecture enables a secure, private environment for developing and running ML workloads, including processing EV charging session data, using Amazon SageMaker Studio. It leverages VPC endpoints and network controls to isolate and protect sensitive data, while allowing selective service access needed for notebook execution and monitoring.

