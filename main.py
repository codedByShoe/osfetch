import os
import platform
import re
import socket
import subprocess
from datetime import datetime

import distro
from cpuinfo import get_cpu_info
import psutil
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from screeninfo import get_monitors

logo = """                   -`
                  .o+`
                 `ooo/
                `+oooo:
               `+oooooo:
               -+oooooo+:
             `/:-:++oooo+:
            `/++++/+++++++:
           `/++++++++++++++:
          `/+++ooooooooooooo/`
         ./ooosssso++osssssso+`
        .oossssso-````/ossssss+`
       -osssssso.      :ssssssso.
      :osssssss/        osssso+++.
     /ossssssss/        +ssssooo/-
   `/ossssso+/:-        -:/+osssso+-
  `+sso+:-`                 `.-/+oso:
 `++:.                           `-/+/
 .`                                 `
 """


def get_uptime() -> str:
    boot_time = psutil.boot_time()
    now = datetime.now().timestamp()

    uptime_seconds = int(now - boot_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{days}d {hours}h {minutes}m"


def get_shell() -> str:
    shell = os.environ.get("SHELL")
    return os.path.basename(shell) if shell else "N/A"


def get_de() -> str:
    de = os.environ.get("DESKTOP_SESSION") or os.environ.get("XDG_CURRENT_DESKTOP")
    return de if de else "N/A"


def get_resolution() -> str:
    try:
        monitors = get_monitors()
        resolutions = [f"{m.width}x{m.height}" for m in monitors]
        return ",".join(resolutions)
    except Exception:
        return "N/A"


def get_packages() -> str:
    try:
        result = subprocess.run(
            ["pacman", "-Q"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            packages = len([line for line in result.stdout.split("\n") if line])
            return f"{packages} (pacman)"
        return "N/A"
    except Exception:
        return "N/A"


def get_os():
    return distro.name(pretty=True)


def get_gpu():
    try:
        result = subprocess.run(
            ["lspci"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        gpu_lines = re.findall(
            r"(VGA compatible controller|3D controller): (.+)",
            result.stdout,
            re.IGNORECASE,
        )
        gpu_names = [gpu[1] for gpu in gpu_lines]
        return ",".join(gpu_names) if gpu_names else "N/A"
    except Exception:
        return "N/A"


def get_cpu():
    info = get_cpu_info()
    cpu = info["brand_raw"]
    return cpu if cpu else "N/A"


def get_ram():
    return f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)}Gib"


def get_host():
    return socket.gethostname()


def get_kernel():
    return platform.release()


def main():
    console = Console()
    os_info = get_os()
    host = get_host()
    kernel = get_kernel()
    uptime = get_uptime()
    packages = get_packages()
    shell = get_shell()
    resolution = get_resolution()
    de = get_de()
    cpu = get_cpu()
    gpu = get_gpu()
    memory = get_ram()

    table = Table(show_header=False, box=None, padding=(0, 1))
    label_color = "bold cyan"
    value_color = "white"

    table.add_row(Text("OS:", style=label_color), Text(os_info, style=value_color))
    table.add_row(Text("Host:", style=label_color), Text(host, style=value_color))
    table.add_row(Text("Kernel:", style=label_color), Text(kernel, style=value_color))
    table.add_row(
        Text("Packages:", style=label_color), Text(packages, style=value_color)
    )
    table.add_row(Text("Uptime:", style=label_color), Text(uptime, style=value_color))
    table.add_row(Text("Shell:", style=label_color), Text(shell, style=value_color))
    table.add_row(Text("DE:", style=label_color), Text(de, style=value_color))
    table.add_row(Text("CPU:", style=label_color), Text(cpu, style=value_color))
    table.add_row(Text("GPU:", style=label_color), Text(gpu, style=value_color))
    table.add_row(Text("Ram:", style=label_color), Text(memory, style=value_color))

    logo_text = Text(logo, style="bold blue")
    logo_panel = Panel.fit(logo_text, padding=(0, 2), box=box.MINIMAL)
    layout = Table.grid(expand=True)
    layout.add_column(justify="left", ratio=3)
    layout.add_column(justify="left", ratio=2)
    layout.add_row(logo_panel, table)

    console.print(Align.left(layout))


if __name__ == "__main__":
    main()
