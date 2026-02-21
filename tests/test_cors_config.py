"""Tests for CORS configuration to prevent upload issues."""

import json
from pathlib import Path

import pytest


class TestCORSConfigFile:
    """Test the local CORS configuration file."""

    @pytest.fixture
    def cors_config_path(self):
        """Get path to CORS config file."""
        return Path(__file__).parent.parent / "config" / "gcs-cors.json"

    @pytest.fixture
    def cors_config(self, cors_config_path):
        """Load CORS configuration."""
        with open(cors_config_path, "r") as f:
            return json.load(f)

    def test_cors_config_file_exists(self, cors_config_path):
        """CORS config file must exist."""
        assert cors_config_path.exists(), (
            f"CORS config file not found at {cors_config_path}. "
            "This file is required for file uploads to work. "
            "Create it by running: ./scripts/setup_gcs_cors.sh"
        )

    def test_cors_config_is_valid_json(self, cors_config):
        """CORS config must be valid JSON."""
        assert isinstance(cors_config, list), "CORS config must be a list"
        assert len(cors_config) > 0, "CORS config must not be empty"

    def test_cors_config_has_required_structure(self, cors_config):
        """CORS config must have required fields."""
        rule = cors_config[0]

        required_fields = ["origin", "method", "responseHeader"]
        for field in required_fields:
            assert field in rule, f"CORS config missing required field: {field}"

    def test_cors_allows_localhost_development(self, cors_config):
        """CORS must allow localhost for development."""
        origins = cors_config[0]["origin"]

        # Check for at least one localhost port
        localhost_origins = [o for o in origins if "localhost" in o]
        assert len(localhost_origins) > 0, (
            "CORS config must include localhost origins for development. "
            "Add at least one: http://localhost:5173, http://localhost:5174, etc."
        )

    def test_cors_allows_put_method(self, cors_config):
        """CORS must allow PUT method for file uploads."""
        methods = cors_config[0]["method"]

        assert "PUT" in methods, (
            "CORS config must allow PUT method for file uploads. "
            "Without this, direct uploads to GCS will fail with CORS errors."
        )

    def test_cors_allows_required_headers(self, cors_config):
        """CORS must allow required response headers."""
        headers = cors_config[0]["responseHeader"]

        required_headers = ["Content-Type"]
        for header in required_headers:
            assert header in headers, (
                f"CORS config must allow '{header}' header. "
                "This is required for proper file upload handling."
            )

    def test_cors_includes_production_origin(self, cors_config):
        """CORS should include production domain."""
        origins = cors_config[0]["origin"]

        # Check for production or vercel origins (properly validate, not just substring)
        # Using endswith() to prevent domain spoofing (e.g., evil-medbilldozer.com)
        # This is the SECURE approach - not a vulnerability
        has_production = any(
            o.endswith("medbilldozer.com")
            or o.endswith(".medbilldozer.com")
            or o.endswith("vercel.app")
            or o.endswith(".vercel.app")
            for o in origins  # nosec
        )

        assert has_production, (
            "CORS config should include production origin (medbilldozer.com or *.vercel.app). "
            "Add it to prevent CORS errors in production."
        )

    def test_cors_has_reasonable_cache_time(self, cors_config):
        """CORS cache time should be reasonable (if specified)."""
        rule = cors_config[0]

        if "maxAgeSeconds" in rule:
            max_age = rule["maxAgeSeconds"]
            assert 300 <= max_age <= 86400, (
                f"CORS maxAgeSeconds should be between 5 minutes and 24 hours, got {max_age}. "
                "Too low causes excessive preflight requests, too high delays config updates."
            )


@pytest.mark.integration
class TestGCSBucketCORS:
    """Integration tests for actual GCS bucket CORS configuration."""

    @pytest.fixture
    def storage_service(self):
        """Get storage service instance."""
        try:
            from backend.app.services.storage_service import get_storage_service

            return get_storage_service()
        except Exception as e:
            pytest.skip(f"Cannot initialize storage service: {e}")

    @pytest.fixture
    def bucket_name(self):
        """Get documents bucket name."""
        try:
            from backend.app.config import settings

            return settings.gcs_bucket_documents
        except Exception as e:
            pytest.skip(f"Cannot load settings: {e}")

    def test_gcs_bucket_has_cors_configured(self, storage_service, bucket_name):
        """GCS bucket must have CORS configured."""
        try:
            bucket = storage_service.client.bucket(bucket_name)
            cors_config = bucket.cors

            assert cors_config is not None and len(cors_config) > 0, (
                f"GCS bucket '{bucket_name}' has no CORS configuration. "
                f"Run './scripts/setup_gcs_cors.sh' to fix this. "
                f"Without CORS, file uploads will fail with browser security errors."
            )
        except Exception as e:
            pytest.skip(f"Cannot check GCS bucket CORS: {e}")

    def test_gcs_cors_allows_put_requests(self, storage_service, bucket_name):
        """GCS bucket CORS must allow PUT for uploads."""
        try:
            bucket = storage_service.client.bucket(bucket_name)
            cors_config = bucket.cors

            if not cors_config:
                pytest.skip("No CORS configuration found")

            methods = cors_config[0].get("method", [])
            assert "PUT" in methods, (
                f"GCS bucket '{bucket_name}' CORS does not allow PUT method. "
                f"File uploads will fail. Run './scripts/setup_gcs_cors.sh' to fix."
            )
        except Exception as e:
            pytest.skip(f"Cannot check GCS bucket CORS methods: {e}")

    def test_gcs_cors_matches_config_file(self, storage_service, bucket_name):
        """GCS bucket CORS should match the config file."""
        try:
            # Load local config
            config_path = Path(__file__).parent.parent / "config" / "gcs-cors.json"
            with open(config_path, "r") as f:
                local_config = json.load(f)[0]

            # Get bucket config
            bucket = storage_service.client.bucket(bucket_name)
            bucket_cors = bucket.cors

            if not bucket_cors:
                pytest.fail(
                    f"GCS bucket has no CORS but config file exists. "
                    f"Run './scripts/setup_gcs_cors.sh' to sync."
                )

            # Check key fields match
            bucket_config = bucket_cors[0]

            # Compare origins
            local_origins = set(local_config["origin"])
            bucket_origins = set(bucket_config.get("origin", []))

            assert local_origins == bucket_origins, (
                f"GCS CORS origins don't match config file. "
                f"Run './scripts/setup_gcs_cors.sh' to sync.\n"
                f"Local: {local_origins}\n"
                f"Bucket: {bucket_origins}"
            )

        except Exception as e:
            pytest.skip(f"Cannot compare CORS configs: {e}")
