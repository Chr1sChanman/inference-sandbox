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
        v1.list_namespaced(_request_timeout=3)
    except (MaxRetryError, ApiException, OSError) as e:
        pytest.skip(f"Kubernetes API unreachable: {type(e).__name__}: {e}")
    return v1

def test_min_running_pods():
    # Loads what kubectl uses ~/.kube/config
    # Minikube automatically creates this when running minikube start
    config.load_kube_config()

    # CoreV1Api to give access to pods, services, etc.
    v1 = client.CoreV1Api()

    # List pods filtered by label using API
    pod_list = v1.list_namespaced_pod(NAMESPACE, label_selector=LABEL_SELECTOR)

    # Extract only running pods
    running_pods = [p for p in pod_list.items if p.status.phase == "Running"]

    print(f"Found {len(running_pods)} running pod(s) with label '{LABEL_SELECTOR}':")
    for pod in running_pods:
        print(f" - {pod.metadata.name}: {pod.status.phase}")

    assert len(running_pods) >= MIN_RUNNING_PODS
