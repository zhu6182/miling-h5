import threading
from typing import Dict, Any

_tasks: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def create_task(task_id: str):
    with _lock:
        _tasks[task_id] = {"status": "processing", "result": None}


def update_task(task_id: str, result: Any):
    with _lock:
        if task_id in _tasks:
            _tasks[task_id]["status"] = "completed"
            _tasks[task_id]["result"] = result


def fail_task(task_id: str, error: str):
    with _lock:
        if task_id in _tasks:
            _tasks[task_id]["status"] = "failed"
            _tasks[task_id]["error"] = error


def get_task(task_id: str) -> Dict[str, Any]:
    with _lock:
        return _tasks.get(task_id, {"status": "not_found"})


def cleanup_task(task_id: str):
    """任务完成后延迟清理，防止内存泄漏"""
    with _lock:
        _tasks.pop(task_id, None)
