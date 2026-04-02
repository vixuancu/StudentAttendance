import argparse
import asyncio
import statistics
import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.config.settings import settings


def _fmt_ms(values: list[float]) -> str:
    if not values:
        return "n/a"
    avg = statistics.mean(values)
    p95 = sorted(values)[max(0, int(len(values) * 0.95) - 1)]
    return f"avg={avg:.2f}ms p95={p95:.2f}ms min={min(values):.2f}ms max={max(values):.2f}ms"


async def run_benchmark(runs: int) -> None:
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )

    connect_times: list[float] = []
    ping_times: list[float] = []
    list_times: list[float] = []

    print("DB URL:", settings.database_url)
    print(f"Runs: {runs}")

    # Warm up
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))

    for _ in range(runs):
        t0 = time.perf_counter()
        async with engine.connect() as conn:
            connect_times.append((time.perf_counter() - t0) * 1000)

            t1 = time.perf_counter()
            await conn.execute(text("SELECT 1"))
            ping_times.append((time.perf_counter() - t1) * 1000)

            t2 = time.perf_counter()
            await conn.execute(
                text(
                    """
                    SELECT id, class_name
                    FROM classrooms
                    WHERE is_cancel = false
                    ORDER BY class_name ASC
                    LIMIT 20
                    """
                )
            )
            list_times.append((time.perf_counter() - t2) * 1000)

    await engine.dispose()

    print("\n=== Benchmark Result ===")
    print("Connect:        ", _fmt_ms(connect_times))
    print("SELECT 1:       ", _fmt_ms(ping_times))
    print("List classrooms:", _fmt_ms(list_times))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quick DB latency benchmark")
    parser.add_argument("--runs", type=int, default=12, help="Number of benchmark runs")
    args = parser.parse_args()

    asyncio.run(run_benchmark(args.runs))
