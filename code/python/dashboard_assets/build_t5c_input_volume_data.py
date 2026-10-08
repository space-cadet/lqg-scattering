#!/usr/bin/env python3
"""Assemble the new T5c source scans into one dashboard data file.

Run from the repository root after the numerical scan records are present:
    python code/python/dashboard_assets/build_t5c_input_volume_data.py
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_paths import DASHBOARD_ROOT, RESULTS_ROOT

ROOT = RESULTS_ROOT
DASHBOARD = DASHBOARD_ROOT


def read_json(name: str) -> dict:
    with (ROOT / name).open(encoding="utf-8") as source:
        return json.load(source)


def complex_pair(real: float, imag: float) -> dict[str, float]:
    return {"real": float(real), "imag": float(imag)}


def project_spread_ratio(sd: float, classical: float) -> float | None:
    if classical <= 1e-14:
        return None
    return float(sd / classical)


def build() -> dict:
    input_scan = read_json("t5c_input_geometry_results.json")
    unequal_scan = read_json("t5c_weighted_shape_results.json")
    selected_j6 = read_json("t5c_weighted_shape_j6_results.json")
    boundary_scan = read_json("t5c_degenerate_limits_results.json")

    input_geometries = []
    for case in input_scan["cases"]:
        target = float(case["classicalVolumeProjectUnitsAtUnitTotalArea"])
        rows = []
        for row in case["results"]:
            rs, al = row["rsToClassicalRatio"], row["alToClassicalRatio"]
            if abs(rs - al) > 1e-10:
                raise ValueError("The calibrated four-valent RS/AL curves disagree")
            normalized_mean = float(row["rsGeometryMatchedMeanOverJ32"])
            normalized_sd = float(row["rsGeometryMatchedSDOverJ32"])
            rows.append(
                {
                    "J": int(row["J"]),
                    "meanRatio": float(rs),
                    "spreadRatio": project_spread_ratio(normalized_sd, target),
                    "meanProjectUnitsOverJ32": normalized_mean,
                    "sdProjectUnitsOverJ32": normalized_sd,
                    "correlationError": float(
                        row["covarianceGeometry"]["maxNormalizedCorrelationError"]
                    ),
                    "areaMeanError": float(row["maxMeanFaceSpinError"]),
                }
            )
        sphere = case["sphereShapeData"]
        input_geometries.append(
            {
                "id": case["name"],
                "label": "Regular" if case["name"] == "regular" else "Unequal skew",
                "areaFractions": case["faceAreaFractions"],
                "vertexCrossRatio": complex_pair(
                    sphere["vertexCrossRatioReal"], sphere["vertexCrossRatioImag"]
                ),
                "classicalVolumeProjectUnits": target,
                "spinorClosureError": float(case["spinorClosureMatrixMaxError"]),
                "faceClosureError": float(case["faceAreaClosureResidual"]),
                "results": rows,
            }
        )

    def shape_row(shape: dict) -> dict:
        sphere = shape["vertexCircumsphereShape"]
        return {
            "pairDiagonal": float(shape["pairDiagonalAtUnitTotalArea"]),
            "bendAngleRadians": float(shape["bendAngleRadians"]),
            "bendAngleDegrees": float(shape["bendAngleRadians"] * 180.0 / 3.141592653589793),
            "areaFractions": shape["faceAreaFractions"],
            "faceNormalCrossRatio": complex_pair(
                shape["faceNormalCrossRatioReal"], shape["faceNormalCrossRatioImag"]
            ),
            "vertexCrossRatio": complex_pair(
                sphere["vertexCrossRatioReal"], sphere["vertexCrossRatioImag"]
            ),
            "unitSphereChordDistances": sphere["unitSphereChordDistances"],
            "classicalVolumeProjectUnits": float(
                shape["results"][0]["rs"]["classicalVolumeProjectUnitsAtUnitTotalArea"]
            ),
            "faceClosureError": float(shape["faceAreaClosureResidual"]),
            "spinorClosureError": float(shape["weightedSpinorClosureMatrixError"]),
            "results": [
                {
                    "J": int(row["J"]),
                    "meanRatio": float(row["rs"]["ratioToClassical"]),
                    "spreadRatio": project_spread_ratio(
                        row["rs"]["geometryMatchedSDOverJ32"],
                        row["rs"]["classicalVolumeProjectUnitsAtUnitTotalArea"],
                    ),
                    "meanProjectUnitsOverJ32": float(
                        row["rs"]["geometryMatchedMeanOverJ32"]
                    ),
                    "sdProjectUnitsOverJ32": float(
                        row["rs"]["geometryMatchedSDOverJ32"]
                    ),
                    "correlationError": float(
                        row["covarianceGeometry"]["maxNormalizedCorrelationError"]
                    ),
                    "areaMeanError": float(row["maxMeanFaceSpinError"]),
                }
                for row in shape["results"]
            ],
        }

    unequal_shapes = [shape_row(shape) for shape in unequal_scan["results"]]
    selected_shapes_j6 = [shape_row(shape) for shape in selected_j6["results"]]
    boundary_rows = [
        {
            "J": int(row["J"]),
            "phiRadians": float(row["phiRadians"]),
            "phiDegrees": float(row["phiRadians"] * 180.0 / 3.141592653589793),
            "classicalVolumeProjectUnits": float(
                row["classicalVolumeProjectUnitsAtUnitTotalArea"]
            ),
            "meanProjectUnitsOverJ32": float(
                row["rs"]["geometryMatchedMeanOverJ32"]
            ),
            "sdProjectUnitsOverJ32": float(
                row["rs"]["geometryMatchedSDOverJ32"]
            ),
            "meanRatio": row["rs"]["ratioToClassical"],
        }
        for row in boundary_scan["results"]
    ]

    output = {
        "model": "Weighted Freidel-Livine input-geometry positive-volume pilot",
        "normalization": {
            "gamma": float(input_scan["normalization"]["gamma"]),
            "hbar": float(input_scan["normalization"]["hbar"]),
            "projectUnits": "(gamma hbar)^(3/2) times the repository positive-volume operator",
            "geometryFactors": input_scan["normalization"]["fixedGeometryMatchingFactors"],
            "ratioDefinition": "kappa * <V>_project / (J^(3/2) * V_classical_project at unit total area)",
            "spreadDefinition": "intrinsic standard deviation of positive volume divided by the same classical target; not a standard error",
            "alSigns": input_scan["normalization"]["alOrientationSignsByLexicographicTriple"],
        },
        "inputGeometries": input_geometries,
        "unequalShapeGrid": {
            "areaFractions": unequal_scan["areaFractions"],
            "diagonals": sorted({shape["pairDiagonal"] for shape in unequal_shapes}),
            "bendAnglesDegrees": sorted({shape["bendAngleDegrees"] for shape in unequal_shapes}),
            "shapes": unequal_shapes,
            "selectedJ6": selected_shapes_j6,
        },
        "flatPath": {
            "areaFractions": boundary_scan["areaFractions"],
            "x": 1.0 / (3.0**0.5),
            "samples": boundary_rows,
        },
        "interpretationLimits": [
            "The input normals label the classical geometry; individual flux-vector means vanish in gauge-invariant FL states.",
            "The normalized covariance correlation matrix is a shape diagnostic and differs from the input normal Gram matrix at finite J for unequal areas.",
            "For the tested four-valent AL signs, geometry-matched RS and AL curves coincide by closure and are not independent evidence.",
            "These finite samples do not establish a large-J limit or either order of the flat-shape and large-J limits.",
        ],
        "sourceFiles": [
            "results/t5c_input_geometry_results.json",
            "results/t5c_weighted_shape_results.json",
            "results/t5c_weighted_shape_j6_results.json",
            "results/t5c_degenerate_limits_results.json",
        ],
    }
    return output


if __name__ == "__main__":
    (DASHBOARD / "t5c-input-volume.json").write_text(
        json.dumps(build(), indent=2) + "\n", encoding="utf-8"
    )
