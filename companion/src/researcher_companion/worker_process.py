import asyncio
import signal


async def run_worker_shell() -> None:
    stop_requested = asyncio.Event()
    install_signal_handlers(stop_requested)
    await stop_requested.wait()


def install_signal_handlers(stop_requested: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()
    for signal_name in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signal_name, stop_requested.set)


if __name__ == "__main__":
    asyncio.run(run_worker_shell())
