import cv2
import numpy as np

FILTER_PARAMS = {
    "floor_hsv_low": np.array([0, 0, 0]),
    "floor_hsv_high": np.array([179, 200, 255]),
    "red_hsv_low": np.array([61, 0, 0]),
    "red_hsv_high": np.array([179, 255, 255]),
    "green_hsv_low": np.array([1, 0, 0]),
    "green_hsv_high": np.array([116, 255, 255]),
    "blue_hsv_low": np.array([0, 2, 2]),
    "blue_hsv_high": np.array([58, 255, 255]),
    "blur_ksize": (5, 5),
    "blur_sigmax": 0,
    "canny_a": 10,
    "canny_b": 50,
    "thresh_thresh": 0,
    "thresh_maxval": 255,
    "corners_gf_maxcorners": 100,
    "corners_gf_qualitylevel": 0.01,
    "corners_gf_mindistance": 10,
    "corners_h_blocksize": 2,
    "corners_h_ksize": 3,
    "corners_h_k": 0.04,
}

COLOR_RANGES = {
    "red": {
        "low": FILTER_PARAMS["red_hsv_low"],
        "high": FILTER_PARAMS["red_hsv_high"],
    },
    "green": {
        "low": FILTER_PARAMS["green_hsv_low"],
        "high": FILTER_PARAMS["green_hsv_high"],
    },
    "blue": {
        "low": FILTER_PARAMS["blue_hsv_low"],
        "high": FILTER_PARAMS["blue_hsv_high"],
    },
}


def mask_ranges(img: np.ndarray, ranges: dict = COLOR_RANGES):
    """
    Apply HSV masks for a set of color ranges.

    Parameters
    ----------
    img : np.ndarray
        RGB image.
    ranges : dict, optional
        Dictionary containing HSV low/high thresholds for each color.

    Returns
    -------
    tuple[np.ndarray, list[str]]
        Masked image and list of detected color names.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    whole_mask = None
    detected_colors = []

    for color_name, color_range in ranges.items():
        mask = cv2.inRange(hsv, color_range["low"], color_range["high"])

        if whole_mask is None:
            whole_mask = mask
        else:
            whole_mask = cv2.bitwise_or(whole_mask, mask)

        if np.any(mask == 255):
            detected_colors.append(color_name)

    masked_img = img.copy()
    masked_img[whole_mask == 255] = 255

    return masked_img, detected_colors


def remove_background(
    img: np.ndarray,
    hsv_low: np.ndarray = FILTER_PARAMS["floor_hsv_low"],
    hsv_high: np.ndarray = FILTER_PARAMS["floor_hsv_high"],
):
    """
    Remove background pixels within a specified HSV range.

    Parameters
    ----------
    img : np.ndarray
        RGB image.
    hsv_low : np.ndarray, optional
        Lower HSV threshold.
    hsv_high : np.ndarray, optional
        Upper HSV threshold.

    Returns
    -------
    np.ndarray
        Foreground image with background removed.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, hsv_low, hsv_high)

    foreground = img.copy()
    foreground[mask > 0] = 0

    return foreground


def get_gray_img(img: np.ndarray, color: int = cv2.COLOR_RGB2GRAY):
    """
    Convert an RGB image to grayscale.

    Parameters
    ----------
    img : np.ndarray
        Input image.
    color : int, optional
        OpenCV color conversion code.

    Returns
    -------
    np.ndarray
        Grayscale image.
    """
    return cv2.cvtColor(img, color)
