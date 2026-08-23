"""
Unit Test Suite for Milestone 9: Production Cloud & CI/CD Deployment.
"""

import os
import unittest


class TestCloudCICD(unittest.TestCase):
    """Unit tests for GitHub Actions workflow, Terraform IaC, and Dockerfiles."""

    def test_github_actions_workflow_exists(self):
        wf_path = os.path.join(os.getcwd(), ".github", "workflows", "ci.yml")
        self.assertTrue(os.path.exists(wf_path))
        with open(wf_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("name: Enterprise Intelligence Platform CI/CD", content)
        self.assertIn("deploy-gcp-cloud-run", content)

    def test_terraform_files_exist(self):
        tf_dir = os.path.join(os.getcwd(), "infrastructure", "terraform")
        self.assertTrue(os.path.exists(os.path.join(tf_dir, "main.tf")))
        self.assertTrue(os.path.exists(os.path.join(tf_dir, "variables.tf")))
        self.assertTrue(os.path.exists(os.path.join(tf_dir, "gcp_resources.tf")))
        self.assertTrue(os.path.exists(os.path.join(tf_dir, "outputs.tf")))

    def test_dockerfiles_exist(self):
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), "backend", "Dockerfile")))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), "frontend", "Dockerfile")))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), "docker-compose.prod.yml")))


if __name__ == "__main__":
    unittest.main()
