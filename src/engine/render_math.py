import math


def ortho(left, right, bottom, top, near, far):
    return [
        2.0 / (right - left),
        0,
        0,
        0,
        0,
        2.0 / (top - bottom),
        0,
        0,
        0,
        0,
        -2.0 / (far - near),
        0,
        -(right + left) / (right - left),
        -(top + bottom) / (top - bottom),
        -(far + near) / (far - near),
        1.0,
    ]


def mat4_identity():
    return [
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
    ]


def mat4_translate(tx: float, ty: float, tz: float = 0.0):
    m = mat4_identity()
    # Column-major: translation is in indices 12..14 (same style as ortho() above)
    m[12] = tx
    m[13] = ty
    m[14] = tz
    return m


def mat4_translate_inv(tx: float, ty: float, tz: float = 0.0):
    # Inverse for pure translation is translation by negative values
    return mat4_translate(-tx, -ty, -tz)


def mat4_scale(sx: float, sy: float, sz: float = 1.0):
    m = mat4_identity()
    m[0] = sx
    m[5] = sy
    m[10] = sz
    return m


def mat4_rotate_z(angle_radians: float):
    c = math.cos(angle_radians)
    s = math.sin(angle_radians)
    return [
        c,
        s,
        0.0,
        0.0,
        -s,
        c,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
    ]


def mat4_mul(a, b):
    # Column-major 4x4: out = a * b
    out = [0.0] * 16
    for col in range(4):
        for row in range(4):
            out[col * 4 + row] = (
                a[0 * 4 + row] * b[col * 4 + 0]
                + a[1 * 4 + row] * b[col * 4 + 1]
                + a[2 * 4 + row] * b[col * 4 + 2]
                + a[3 * 4 + row] * b[col * 4 + 3]
            )
    return out


def build_view_proj(fb_w: int, fb_h: int, cam_x: float, cam_y: float):
    projection = ortho(
        -fb_w / 2,
        fb_w / 2,
        -fb_h / 2,
        fb_h / 2,
        -1.0,
        1.0,
    )

    view = mat4_translate_inv(cam_x, cam_y, 0.0)
    return mat4_mul(projection, view)


def build_model(pos_x: float, pos_y: float, rot_rad: float, scale_x: float, scale_y: float):
    t = mat4_translate(pos_x, pos_y, 0.0)
    r = mat4_rotate_z(rot_rad)
    s = mat4_scale(scale_x, scale_y, 1.0)
    return mat4_mul(t, mat4_mul(r, s))
