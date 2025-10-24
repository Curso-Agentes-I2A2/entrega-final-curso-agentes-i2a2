from locust import HttpUser, task, between
import os

class AuditUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def upload_invoice(self):
        fixture_path = os.getenv("SAMPLE_NF_PATH", "tests/fixtures/sample_nf.xml")
        with open(fixture_path, "rb") as f:
            self.client.post("/api/invoices/upload", files={"file": ("nf.xml", f, "application/xml")})

    @task(2)
    def get_audit_status(self):
        # This expects at least one audit id present (adjust for realistic load)
        self.client.get("/api/audits/1")

    @task(3)
    def list_invoices(self):
        self.client.get("/api/invoices")
