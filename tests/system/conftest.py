from __future__ import annotations

import pytest
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException
from urllib3.exceptions import MaxRetryError


@pytest.fixture(scope="session")
def k8s_v1():
    """Yield CoreV1Api or skip if cluster unreachable"""
    try:
        config.load_kube_config()
    except ConfigException as e:
        pytest.skip(f"No usable kubeconfig: {e}")
    
    """Fast reachability check vs default 3x retries for 45s"""
    v1 = client.CoreV1Api()
    try:
        v1.list_namespace(_request_timeout=3)
    except (MaxRetryError, ApiException, OSError) as e:
        pytest.skip(f"Kubernetes API unreachable: {type(e).__name__}: {e}")
    return v1