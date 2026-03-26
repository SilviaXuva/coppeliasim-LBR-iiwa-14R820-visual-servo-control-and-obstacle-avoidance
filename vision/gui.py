import cv2
import numpy as np

BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 100, 255)
BLACK = (0, 0, 0)


def write_text(
    img: np.ndarray,
    text,
    origin,
    font_face=cv2.FONT_HERSHEY_SIMPLEX,
    font_scale: float = 1,
    color=PINK,
    thickness: int = 1,
) -> None:
    """
    Draw text on an image.

    Parameters
    ----------
    img : np.ndarray
        Target image.
    text : object
        Text content to be drawn.
    origin : tuple
        Bottom-left corner of the text.
    font_face : int, optional
        OpenCV font type.
    font_scale : float, optional
        Font scale factor.
    color : tuple, optional
        Text color in BGR format.
    thickness : int, optional
        Text thickness.
    """
    cv2.putText(img, str(text), origin, font_face, font_scale, color, thickness)


def draw_circle(
    img: np.ndarray,
    center,
    radius: int = 3,
    color=PINK,
    thickness: int = -1,
) -> None:
    """
    Draw a circle on an image.

    Parameters
    ----------
    img : np.ndarray
        Target image.
    center : tuple
        Circle center coordinates.
    radius : int, optional
        Circle radius.
    color : tuple, optional
        Circle color in BGR format.
    thickness : int, optional
        Circle thickness. Use -1 to fill the circle.
    """
    cv2.circle(img, center, radius, color, thickness)


def draw_rectangle(
    img: np.ndarray,
    pt1,
    pt2,
    color=PINK,
    thickness: int = 2,
) -> None:
    """
    Draw a rectangle on an image.

    Parameters
    ----------
    img : np.ndarray
        Target image.
    pt1 : tuple
        First corner point.
    pt2 : tuple
        Opposite corner point.
    color : tuple, optional
        Rectangle color in BGR format.
    thickness : int, optional
        Rectangle border thickness.
    """
    cv2.rectangle(img, pt1, pt2, color, thickness)


def draw_contours(
    img: np.ndarray,
    contours,
    contour_idx: int = -1,
    color=PINK,
    thickness: int = 3,
) -> None:
    """
    Draw contours on an image.

    Parameters
    ----------
    img : np.ndarray
        Target image.
    contours : list
        List of contours.
    contour_idx : int, optional
        Contour index to draw. Use -1 to draw all contours.
    color : tuple, optional
        Contour color in BGR format.
    thickness : int, optional
        Contour thickness.
    """
    cv2.drawContours(img, contours, contour_idx, color, thickness)


def draw_axes(img: np.ndarray, mtx, dist_coeff, rvec, tvec, length) -> None:
    """
    Draw 3D axes on an image.

    Parameters
    ----------
    img : np.ndarray
        Target image.
    mtx : np.ndarray
        Camera intrinsic matrix.
    dist_coeff : np.ndarray | None
        Distortion coefficients.
    rvec : np.ndarray
        Rotation vector.
    tvec : np.ndarray
        Translation vector.
    length : float
        Axis length.
    """
    cv2.drawFrameAxes(img, mtx, dist_coeff, rvec, tvec, length)


def show_img(window_name: str, img: np.ndarray) -> None:
    """
    Display an image in an OpenCV window.

    Parameters
    ----------
    window_name : str
        Window title.
    img : np.ndarray
        Image to be displayed.
    """
    cv2.imshow(window_name, img)
    cv2.waitKey(1)


def save_img(file_path: str, img: np.ndarray) -> None:
    """
    Save an image to disk.

    Parameters
    ----------
    file_path : str
        Output image path.
    img : np.ndarray
        Image to be saved.
    """
    cv2.imwrite(file_path, img)
