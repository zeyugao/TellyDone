from typing import List, Dict
import os
import time
import apprise


def proc_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_process_name(pid: int) -> str:
    """Get the full command line of a process by PID."""
    try:
        with open(f"/proc/{pid}/cmdline", "r") as f:
            cmdline = f.read().replace('\0', ' ').strip()
            return cmdline if cmdline else f"PID {pid}"
    except (FileNotFoundError, PermissionError, OSError):
        return f"PID {pid}"


def watch(config: Dict, pid: int):
    apprise_url_list = config.get("apprise_url", [])
    watch_config = config.get("watch", {})
    continuous = watch_config.get("continuous", False)
    interval = watch_config.get("interval", 1800)
    include_full_process_name = watch_config.get("include_full_process_name", True)

    last_check = 0

    notifier = apprise.Apprise()
    for apprise_url in apprise_url_list:
        notifier.add(apprise_url)
    notifier.add(config)

    # Get process name at the beginning if needed
    process_name = get_process_name(pid) if include_full_process_name else None

    start_time = time.time()
    while True:
        if proc_alive(pid):
            time.sleep(0.1)
        else:
            break
        current_time = time.time()

        if current_time - last_check > interval:
            if continuous:
                if include_full_process_name and process_name:
                    title = f"Process still alive: {process_name}"
                else:
                    title = f"Process {pid} is still alive"
                notifier.notify(
                    title=title,
                    body=f"Runned for {current_time - start_time: .2f} seconds.",
                )
            last_check = (current_time // interval) * interval
    end_time = time.time()

    # Send completion notification
    if include_full_process_name and process_name:
        title = f"Process finished: {process_name}"
        body = f"Command: {process_name}\nRunned for {end_time - start_time: .2f} seconds."
    else:
        title = f"Process {pid} finished"
        body = f"Runned for {end_time - start_time: .2f} seconds."

    notifier.notify(title=title, body=body)


if __name__ == "__main__":
    pass
