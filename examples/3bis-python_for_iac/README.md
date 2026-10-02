# Example 4: Why Use Python for Infrastructure as Code (IaC)?

This example demonstrates **5 key reasons** why using a high-level general-purpose language like **Python with Pulumi** provides significantly more freedom, flexibility, and capabilities than domain-specific languages like **Terraform with HCL**.

---

## The 5 Python for IaC Highlights

1. **Native Control Flow (`if/else` & `for` loops):**
   - Uses `if/else` logic based on `pulumi.get_stack()` (`dev` vs `prod`) to set VM machine types (`e2-micro` vs `e2-medium`).
   - Uses a standard Python `for` loop to dynamically create 3 GCP Compute Engine VM instances (`gcp.compute.Instance`).

2. **Dynamic HTTP / REST API Requests (`requests`):**
   - Uses the `requests` library at runtime to fetch the deployer's public IP address from `https://api.ipify.org` and dynamically restrict firewall access.

3. **External Data Ingestion & Validation (`csv` & `try/except`):**
   - Parses firewall rule specifications from local `firewall_rules.csv`.
   - Includes data validation (checking header schema, required fields, and integer port range `1–65535`) wrapped in a Python `try/except` block with `pulumi.log` reporting.

4. **Object-Oriented Abstraction (`ComponentResource`):**
   - Encapsulates network creation (VPC, Subnetwork, and Firewall rules) into a custom, reusable class `SecureGcpNetwork` subclassing `pulumi.ComponentResource`.

5. **In-Memory Unit Testing & Mocking (`pytest`):**
   - Includes `test_infra.py` using `pulumi.runtime.set_mocks()` and `pytest` to test infrastructure logic locally in milliseconds without deploying resources to GCP.

---

## How to Run

### 1. Run Unit Tests (No Cloud Connection Required)
```bash
pytest test_infra.py
```

### 2. Preview Infrastructure Changes
```bash
pulumi preview
```

### 3. Deploy Infrastructure
```bash
pulumi up
```
