import numpy as np


headers = [
    "car_size", "car_width", "car_len", "ramp_angle",
    "front_bumper_length", "wind_screen_x", "wind_screen_z",
    "side_mirrors_x", "side_mirrors_z", "rear_window_x",
    "rear_window_z", "trunklid_angle", "trunklid_x",
    "trunklid_z", "diffusor_angle", "car_green_house_angle",
    "car_front_hood_angle", "car_air_intake_angle",
    "tires_diameter", "tires_width",
]


def make_goal1_notchback_samples():
    """Small deterministic dry-run DOE for goal 1."""
    width_len_pairs = [
        (-0.10, -0.10),
        (-0.10, 0.10),
        (0.10, -0.10),
        (0.10, 0.10),
    ]

    sample = np.zeros((len(width_len_pairs), len(headers)))
    sample[:, headers.index("car_size")] = 1.0

    for row, (car_width, car_len) in enumerate(width_len_pairs):
        sample[row, headers.index("car_width")] = car_width
        sample[row, headers.index("car_len")] = car_len

    return sample


if __name__ == "__main__":
    np.savetxt(
        "lhs_parameters_Notch_v3.csv",
        make_goal1_notchback_samples(),
        delimiter=",",
        header=",".join(headers),
        comments="",
        fmt="%.8g",
    )
