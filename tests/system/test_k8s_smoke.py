import pytest
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException
from urllib3.exceptions import MaxRetryError

pytestmark = pytest.mark.system

NAMESPACE = "default"
LABEL_SELECTOR = "app=inference-sandbox"
MIN_RUNNING_PODS = 2

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

@pytest.mark.k8s
def test_min_running_pods(k8s_v1):
    pods = k8s_v1.list_namespaced_pod(
        NAMESPACE, label_selector=LABEL_SELECTOR, _request_timeout=5
    ).items
    running = [p for p in pods if p.status.phase == "Running"]
    names = [p.metadata.name for p in running]
    assert len(running) >= MIN_RUNNING_PODS, (
        f"Expected >= {MIN_RUNNING_PODS} Running pods with "
        f"label '{LABEL_SELECTOR!r}'; found {len(running)}: {names}"
    )
