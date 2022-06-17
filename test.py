import math
from typing import List

# Lens constants assuming a 1080p image
f = 714.285714
center = [960, 540]
D = 1.082984  # For image-1, switch to 0.871413 for image-2


def cartesian2sphere(pt):
    x = (pt[0] - center[0]) / f
    y = (pt[1] - center[1]) / f

    r = math.sqrt(x*x + y*y)
    if r != 0:
        x /= r
        y /= r
    r *= D
    sin_theta = math.sin(r)
    x *= sin_theta
    y *= sin_theta
    z = math.cos(r)

    return [x, y, z]


def sphere2cartesian(pt):
    r = math.acos(pt[2])
    r /= D
    if pt[2] != 1:
        r /= math.sqrt(1 - pt[2] * pt[2])
    x = r * pt[0] * f + center[0]
    y = r * pt[1] * f + center[1]
    return [x, y]


def convert_point(point: List[int]) -> List[int]:
    """Convert single points between Cartesian and spherical coordinate systems"""
    if len(point) == 2:
        return cartesian2sphere(point)
    elif len(point) == 3:
        return sphere2cartesian(point)
    else:
        raise ValueError(f'Expected point to be 2 or 3D, got {len(point)} dimensions')


class CartesianBbox:

    def __init__(self, points: List[int], fmt: str):
        assert fmt in ['xyxy', 'xywh', 'cxcywh'], 'Invalid bbox format'
        assert len(points) == 4, 'Cartesian bbox must have 4 values'
        self.points = points
        self.fmt = fmt

    def get_corner_points(self):
        corner_points = []
        points = self.points.copy()

        if self.fmt == 'cxcywh':
            points[0] = int(points[0] - (points[2] / 2))
            points[1] = int(points[1] - (points[3] / 2))

        if self.fmt[-2:] == 'wh':
            points[2] = points[0] + points[2]
            points[3] = points[1] + points[3]

        corner_points.append([points[0], points[1]])
        corner_points.append([points[2], points[1]])
        corner_points.append([points[2], points[3]])
        corner_points.append([points[0], points[3]])

        return corner_points


class SphericalBbox:

    def __init__(self):
        self.points = []

    def convert(self, bbox): # bbox(diagonal points -> center, radius)
        self.points = [convert_point(pt) for pt in bbox.get_corner_points()]
        return self.points

    def __call__(self, bbox):
        return self.convert(bbox)


def bbox_to_spherical(cartesian: CartesianBbox) -> SphericalBbox:
    return SphericalBbox()(cartesian)


class CartesianPolygon:

    def __init__(self, points=[]):
        self.points = points

    def add_points(self, points):
        self.points += points


class SphericalPolygon:

    def __init__(self, points=[]):
        self.points = points

    def add_points(self, points):
        if not isinstance(points[0], list):
            points = [points]
        self.points += points


def polygon_to_spherical(cartesian: CartesianPolygon) -> SphericalPolygon:
    spherical_poly = SphericalPolygon()
    for cat in cartesian.points:
        spl = convert_point(cat)
        spherical_poly.add_points(spl) # r, theta, phi
    return spherical_poly


if __name__=='__main__':
    cbox = CartesianBbox([30, 30, 20, 20], 'cxcywh')
    sbox = bbox_to_spherical(cbox)
    print (cbox.points)
    print (cbox.get_corner_points())
    print (sbox)

    cart_poly = CartesianPolygon([[30, 30], [10, 60], [50, 60]])
    sphl_poly = polygon_to_spherical(cart_poly)

    print ('cartesian polygon:', cart_poly.points)
    print ('spherical polygon:', sphl_poly.points)
