"""Build, prove, and verify a tiny ONNX MLP with EZKL.

This is a reproducibility prototype, not an evaluation of a production model.
It records wall-clock timings and artifact sizes for the exact local machine.
Run from the repository root:

    PYTHONPATH=zkml-prototype/.deps python3 zkml-prototype/run_tiny_mlp.py
"""

from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

import ezkl
import numpy as np
import onnx
from onnx import TensorProto, checker, helper, numpy_helper


ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"


def timed(label: str, action):
    started = time.perf_counter()
    result = action()
    elapsed = time.perf_counter() - started
    print(f"{label}: {elapsed:.3f} s")
    return result, elapsed


def create_model(path: Path) -> None:
    """Create a deterministic 2-input, 2-output affine-ReLU ONNX model."""
    x = helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 2])
    y = helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 2])
    weights = numpy_helper.from_array(
        np.array([[0.50, -0.25], [0.75, 0.50]], dtype=np.float32), name="weights"
    )
    bias = numpy_helper.from_array(np.array([0.10, -0.20], dtype=np.float32), name="bias")
    graph = helper.make_graph(
        [
            helper.make_node("Gemm", ["input", "weights", "bias"], ["linear"]),
            helper.make_node("Relu", ["linear"], ["output"]),
        ],
        "tiny_affine_relu",
        [x],
        [y],
        [weights, bias],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    checker.check_model(model)
    onnx.save(model, path)


def main() -> None:
    ARTIFACTS.mkdir(exist_ok=True)
    model = ARTIFACTS / "tiny_mlp.onnx"
    data = ARTIFACTS / "input.json"
    settings = ARTIFACTS / "settings.json"
    compiled = ARTIFACTS / "tiny_mlp.ezkl"
    witness = ARTIFACTS / "witness.json"
    srs = ARTIFACTS / "kzg.srs"
    vk = ARTIFACTS / "vk.key"
    pk = ARTIFACTS / "pk.key"
    proof = ARTIFACTS / "proof.json"

    create_model(model)
    data.write_text(json.dumps({"input_data": [[0.25, -0.75]]}), encoding="utf-8")

    timings = {}
    _, timings["settings_s"] = timed("generate settings", lambda: ezkl.gen_settings(str(model), str(settings)))
    _, timings["calibration_s"] = timed(
        "calibrate settings",
        lambda: ezkl.calibrate_settings(str(data), str(model), str(settings), target="resources"),
    )
    # The calibrator defaults to UNSAFE checking for development convenience.
    # A proof reported by this prototype must use safe circuit checks instead.
    settings_data = json.loads(settings.read_text(encoding="utf-8"))
    settings_data["run_args"]["check_mode"] = "SAFE"
    settings_data["check_mode"] = "SAFE"
    settings.write_text(json.dumps(settings_data, indent=2) + "\n", encoding="utf-8")
    _, timings["compile_s"] = timed(
        "compile circuit", lambda: ezkl.compile_circuit(str(model), str(compiled), str(settings))
    )
    # Locally generated SRS is suitable only for this reproducibility smoke test.
    # A deployed protocol must use a ceremony-derived public SRS.
    _, timings["srs_s"] = timed(
        "generate test SRS", lambda: ezkl.gen_srs(str(srs), settings_data["run_args"]["logrows"])
    )
    _, timings["witness_s"] = timed(
        "generate witness", lambda: ezkl.gen_witness(str(data), str(compiled), str(witness))
    )
    _, timings["setup_s"] = timed(
        "setup",
        lambda: ezkl.setup(str(compiled), str(vk), str(pk), str(srs), witness_path=str(witness)),
    )
    proved, timings["prove_s"] = timed(
        "prove", lambda: ezkl.prove(str(witness), str(compiled), str(pk), str(proof), str(srs))
    )
    verified, timings["verify_s"] = timed(
        "verify", lambda: ezkl.verify(str(proof), str(settings), str(vk), str(srs))
    )

    output = {
        "scope": (
            "One deterministic affine-ReLU ONNX model; local EZKL proof/verification "
            "smoke test, not a benchmark. The SRS is locally generated for testing and "
            "must not be used by a deployed protocol."
        ),
        "toolchain": {"ezkl": ezkl.__version__, "python": sys.version, "platform": platform.platform()},
        "model": {"architecture": "Gemm(2x2) -> ReLU", "input": [[0.25, -0.75]]},
        "proof_created": bool(proved),
        "proof_verified": bool(verified),
        "timings_seconds": {name: round(value, 6) for name, value in timings.items()},
        "artifact_bytes": {path.name: path.stat().st_size for path in (model, settings, compiled, witness, srs, vk, pk, proof)},
    }
    results = ROOT / "results.json"
    results.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    print("Wrote", results)


if __name__ == "__main__":
    main()
