import sys
import threading
import time

from finance_cli.providers.base import quiet_call


def noisy(label: str) -> str:
    print(f"noise from {label}")
    print(f"error noise from {label}", file=sys.stderr)
    time.sleep(0.05)
    return label


def test_concurrent_quiet_calls_restore_the_real_streams():
    real_stdout, real_stderr = sys.stdout, sys.stderr
    barrier = threading.Barrier(4)

    def run(label: str) -> None:
        barrier.wait()
        assert quiet_call(noisy, label) == label

    threads = [threading.Thread(target=run, args=(str(index),)) for index in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sys.stdout is real_stdout
    assert sys.stderr is real_stderr


def test_quiet_call_silences_only_its_own_thread(capsys):
    started, release = threading.Event(), threading.Event()

    def slow_noisy() -> None:
        started.set()
        release.wait(2)
        print("should be hidden")

    worker = threading.Thread(target=quiet_call, args=(slow_noisy,))
    worker.start()
    started.wait(2)
    print("main thread still prints")
    release.set()
    worker.join()
    out = capsys.readouterr().out
    assert "main thread still prints" in out
    assert "should be hidden" not in out
