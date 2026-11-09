"""Measure `POST /research` latency against the 5-second requirement (#8).

    python -m agentic_research.agent.bench --url http://127.0.0.1:8001 --n 20

Sends the fixed questions round-robin, one request at a time, and reports
p50/p95/max of the end-to-end HTTP time.
"""

import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter

import httpx

from .evaluate import percentile95

LIMIT_S = 5.0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://127.0.0.1:8001")
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument(
        "--questions", type=Path, default=Path("evaluation/questions.json")
    )
    args = parser.parse_args(argv)
    questions = json.loads(args.questions.read_text(encoding="utf-8"))

    seconds: list[float] = []
    with httpx.Client(base_url=args.url, timeout=60) as client:
        for i in range(args.n):
            started = perf_counter()
            response = client.post("/research", json=questions[i % len(questions)])
            elapsed = perf_counter() - started
            response.raise_for_status()
            seconds.append(elapsed)

    ordered = sorted(seconds)
    p95 = percentile95(seconds)
    over = sum(s > LIMIT_S for s in seconds)
    print(
        f"n={len(seconds)} p50={median(seconds):.2f}s p95={p95:.2f}s "
        f"max={ordered[-1]:.2f}s over_{LIMIT_S:g}s={over}"
    )


if __name__ == "__main__":
    main()
