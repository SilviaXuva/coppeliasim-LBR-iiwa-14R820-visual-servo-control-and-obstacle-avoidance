from __future__ import annotations

from manipulator_framework.application.dto.run_requests import RunPBVSProtocolRequest
from manipulator_framework.application.use_cases.run_pbvs_protocol import RunPBVSProtocol


def main(
    protocol_path: str = "experiments/configs/pbvs_with_avoidance_protocol.yaml",
) -> int:
    response = RunPBVSProtocol().execute(
        RunPBVSProtocolRequest(protocol_path=protocol_path)
    )

    for index, run in enumerate(response.runs, start=1):
        print(
            f"[RUN {index}/{response.repetitions}] "
            f"run_id={run.run_id} success={run.success} "
            f"final_visual_error={run.final_visual_error} "
            f"minimum_clearance={run.minimum_clearance}"
        )

    print(f"[OK] Baseline protocol completed. run_ids={list(response.run_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
