from __future__ import annotations

import pytest

NAMESPACE = "default"
LABEL_SELECTOR = "app=inference-sandbox"
MIN_RUNNING_PODS = 2

@pytest.mark.system
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
