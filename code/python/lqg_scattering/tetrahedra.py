"""Closed tetrahedron families, face vectors, and reconstruction helpers."""

import itertools
import math

import numpy as np

from .conventions import GAMMA

GEOMETRY_MATCHING_FACTORS = {
    # For a closed four-valent vertex, convert repository project units to
    # the classical tetrahedron volume convention used by the T5c comparisons.
    "rs": math.sqrt(2.0) / 12.0,
    "al": math.sqrt(2.0) / 6.0,
}

TETRAHEDRON_NORMALS = np.array(
    [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=float
) / np.sqrt(3.0)


def closed_equal_area_normals(x, phi):
    """Construct four unit normals with sum zero, away from endpoints."""
    if not 0.0 < x < 1.0:
        raise ValueError("x must be strictly between 0 and 1")
    transverse = math.sqrt(1.0 - x * x)
    return np.array(
        [
            [transverse, 0.0, x],
            [-transverse, 0.0, x],
            [transverse * math.cos(phi), transverse * math.sin(phi), -x],
            [-transverse * math.cos(phi), -transverse * math.sin(phi), -x],
        ],
        dtype=float,
    )

def tetrahedron_vertices(x, phi):
    """Reconstruct a unit-face-area tetrahedron from its outward normals."""
    normals = closed_equal_area_normals(x, phi)
    face_vectors = normals[[1, 2, 3]].copy()
    determinant = float(np.linalg.det(face_vectors))
    if determinant > 0:
        face_vectors[[1, 2]] = face_vectors[[2, 1]]
        determinant = -determinant
    if determinant >= -1e-12:
        raise ValueError("cannot draw a degenerate tetrahedron")

    six_volume = math.sqrt(-8.0 * determinant)
    edge_a = 4.0 * np.cross(face_vectors[1], face_vectors[2]) / six_volume
    edge_b = 4.0 * np.cross(face_vectors[2], face_vectors[0]) / six_volume
    edge_c = 4.0 * np.cross(face_vectors[0], face_vectors[1]) / six_volume
    vertices = np.array([[0.0, 0.0, 0.0], edge_a, edge_b, edge_c])
    return vertices - np.mean(vertices, axis=0)

def face_area_vectors(vertices):
    """Return outward face-area vectors, ordered by opposite vertex."""
    points = np.asarray(vertices, dtype=float)
    if points.shape != (4, 3):
        raise ValueError("vertices must have shape (4, 3)")
    faces = np.zeros((4, 3), dtype=float)
    for opposite in range(4):
        ids = [i for i in range(4) if i != opposite]
        p0, p1, p2 = points[ids]
        area_vector = 0.5 * np.cross(p1 - p0, p2 - p0)
        face_center = (p0 + p1 + p2) / 3.0
        if np.dot(area_vector, face_center - points[opposite]) < 0.0:
            area_vector = -area_vector
        faces[opposite] = area_vector
    return faces

def closed_face_vectors_from_shape(area_fractions, diagonal, phi):
    """Construct closed tetrahedral face vectors at fixed area fractions.

    The diagonal is |F0+F1| in unit-total-area variables. It and the bend
    angle phi give two shape coordinates after quotienting common rotations.
    """
    areas = np.asarray(area_fractions, dtype=float)
    if areas.shape != (4,) or np.any(areas <= 0.0):
        raise ValueError("area_fractions must contain four positive values")
    if not np.isclose(areas.sum(), 1.0, atol=1e-12, rtol=0.0):
        raise ValueError("area_fractions must sum to one")
    lower = max(abs(areas[0] - areas[1]), abs(areas[2] - areas[3]))
    upper = min(areas[0] + areas[1], areas[2] + areas[3])
    if not lower < diagonal < upper:
        raise ValueError(f"diagonal must lie strictly between {lower} and {upper}")

    d = float(diagonal)
    z0 = (d * d + areas[0] ** 2 - areas[1] ** 2) / (2.0 * d)
    z1 = d - z0
    z2 = (areas[3] ** 2 - areas[2] ** 2 - d * d) / (2.0 * d)
    z3 = -d - z2
    r0_squared = areas[0] ** 2 - z0 * z0
    r2_squared = areas[2] ** 2 - z2 * z2
    if min(r0_squared, r2_squared) <= 0.0:
        raise ValueError("shape lies on a degenerate pair-triangle boundary")
    r0, r2 = math.sqrt(r0_squared), math.sqrt(r2_squared)
    c, s = math.cos(phi), math.sin(phi)
    faces = np.array([
        [r0, 0.0, z0],
        [-r0, 0.0, z1],
        [r2 * c, r2 * s, z2],
        [-r2 * c, -r2 * s, z3],
    ])
    if np.max(np.abs(np.linalg.norm(faces, axis=1) - areas)) > 1e-11:
        raise ArithmeticError("constructed face-vector lengths miss area labels")
    if np.linalg.norm(faces.sum(axis=0)) > 1e-11:
        raise ArithmeticError("constructed face vectors failed closure")
    return faces

def classical_volume_from_faces(face_vectors):
    """Tetrahedron volume from any three faces meeting at a vertex."""
    faces = np.asarray(face_vectors, dtype=float)
    if faces.shape != (4, 3):
        raise ValueError("face_vectors must have shape (4, 3)")
    closure = np.linalg.norm(faces.sum(axis=0))
    if closure > 1e-10:
        raise ValueError(f"face vectors do not close: {closure:.3e}")
    determinant = abs(float(np.linalg.det(faces[[1, 2, 3]])))
    return math.sqrt((2.0 / 9.0) * determinant)

def circumsphere_shape_data(vertices):
    """Return unit-sphere vertices, their complex cross-ratio, and chords."""
    points = np.asarray(vertices, dtype=float)
    edges = points[1:] - points[0]
    center = np.linalg.solve(
        2.0 * edges,
        np.sum(points[1:] ** 2, axis=1) - float(np.dot(points[0], points[0])),
    )
    radius = float(np.linalg.norm(points[0] - center))
    if radius <= 0.0:
        raise ValueError("tetrahedron has a zero circumradius")
    sphere_points = (points - center) / radius

    # Pick a stereographic pole that is not close to any vertex.
    axes = np.vstack((np.eye(3), -np.eye(3)))
    pole = axes[int(np.argmax(np.min(1.0 + sphere_points @ axes.T, axis=0)))]
    seed = np.eye(3)[int(np.argmin(np.abs(pole)))]
    e1 = np.cross(pole, seed)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(pole, e1)
    denominator = 1.0 + sphere_points @ pole
    if np.min(denominator) <= 1e-12:
        raise ArithmeticError("stereographic projection hit its pole")
    z = (sphere_points @ e1 + 1j * (sphere_points @ e2)) / denominator
    cross_ratio = ((z[0] - z[2]) * (z[1] - z[3])) / (
        (z[0] - z[3]) * (z[1] - z[2])
    )
    chords = {
        f"{i}{j}": float(np.linalg.norm(sphere_points[i] - sphere_points[j]))
        for i, j in itertools.combinations(range(4), 2)
    }
    return {
        "circumcenter": center.tolist(),
        "circumradius": radius,
        "unitSphereVertices": sphere_points.tolist(),
        "tetrahedronVolumeAtUnitCircumradius": abs(float(np.linalg.det(
            sphere_points[1:] - sphere_points[0]
        ))) / 6.0,
        "unitSphereRadiusResidual": float(np.max(np.abs(
            np.linalg.norm(sphere_points, axis=1) - 1.0
        ))),
        "vertexCrossRatioReal": float(cross_ratio.real),
        "vertexCrossRatioImag": float(cross_ratio.imag),
        "unitSphereChordDistances": chords,
    }

def tetrahedron_from_face_vectors(face_vectors):
    """Recover vertices and volume from four closed tetrahedral area vectors."""
    faces = np.asarray(face_vectors, dtype=float)
    if faces.shape != (4, 3):
        raise ValueError("expected four three-dimensional face vectors")
    if np.linalg.norm(faces.sum(axis=0)) > 1e-8:
        raise ValueError("face-area vectors do not close")

    # The chosen three faces meet at one vertex.  An O(3) reflection preserves
    # the Gram matrix and fixes the sign convention used by the dual formula.
    triple = faces[[1, 2, 3]].copy()
    determinant = float(np.linalg.det(triple))
    if determinant > 0.0:
        faces[:, 2] *= -1.0
        triple[:, 2] *= -1.0
        determinant = -determinant
    if determinant >= -1e-12:
        raise ValueError("covariance geometry is degenerate")

    dual_scale = math.sqrt(-8.0 * determinant)
    edges = np.array(
        [
            4.0 * np.cross(triple[1], triple[2]) / dual_scale,
            4.0 * np.cross(triple[2], triple[0]) / dual_scale,
            4.0 * np.cross(triple[0], triple[1]) / dual_scale,
        ]
    )
    vertices = np.vstack((np.zeros(3), edges))
    volume = abs(float(np.linalg.det(edges))) / 6.0

    # Check that the reconstructed tetrahedron has the requested outward
    # area vectors, with face i opposite vertex i.
    reconstructed = np.zeros((4, 3))
    for opposite in range(4):
        ids = [index for index in range(4) if index != opposite]
        p0, p1, p2 = vertices[ids]
        area_vector = 0.5 * np.cross(p1 - p0, p2 - p0)
        face_center = (p0 + p1 + p2) / 3.0
        if np.dot(area_vector, face_center - vertices[opposite]) < 0.0:
            area_vector = -area_vector
        reconstructed[opposite] = area_vector
    return vertices, volume, reconstructed

def reconstruct_from_gram(gram):
    """Factor a rank-three closed Gram matrix and reconstruct its tetrahedron."""
    values, vectors = np.linalg.eigh(0.5 * (gram + gram.T))
    scale = max(1.0, float(np.max(np.abs(values))))
    tol = 128.0 * np.finfo(float).eps * scale
    if values[0] < -tol or abs(values[0]) > 1e-8 * scale:
        raise ValueError(f"Gram matrix is not closed/positive semidefinite: {values}")
    if values[1] <= tol:
        raise ValueError("Gram matrix has fewer than three nondegenerate directions")

    face_vectors = vectors[:, 1:] * np.sqrt(values[1:])[None, :]
    vertices, volume_j_units, reconstructed = tetrahedron_from_face_vectors(face_vectors)
    gram_error = float(np.max(np.abs(reconstructed @ reconstructed.T - gram)))
    return {
        "gramEigenvalues": values.tolist(),
        "rmsFaceAreasJUnits": np.sqrt(np.maximum(np.diag(gram), 0.0)).tolist(),
        "verticesJUnits": vertices.tolist(),
        "volumeJUnits": volume_j_units,
        "volumeProjectUnits": volume_j_units * GAMMA**1.5,
        "reconstructedFaceGramMaxAbsError": gram_error,
    }

__all__ = [
    "TETRAHEDRON_NORMALS", "GEOMETRY_MATCHING_FACTORS",
    "closed_equal_area_normals", "tetrahedron_vertices",
    "face_area_vectors", "closed_face_vectors_from_shape",
    "classical_volume_from_faces", "circumsphere_shape_data",
    "tetrahedron_from_face_vectors", "reconstruct_from_gram",
]
