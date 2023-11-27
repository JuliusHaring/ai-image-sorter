from datetime import datetime
from glob import glob

import pytest
import shutil
import os
from image_analysis import (
    _extract_geolocation,
    _extract_date,
    _get_exif_data,
    _resolve_gps_to_place,
)


@pytest.fixture
def create_test_files(tmp_path):
    # Create a temporary input directory
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    # Copy the test image to the temporary input directory
    test_image_path = os.path.join("test", "assets", "IMG_0736.jpeg")
    shutil.copy(test_image_path, input_dir)

    # Create a temporary output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    return input_dir, output_dir


def test_image_analysis_tools(create_test_files):
    input_dir, output_dir = create_test_files

    for image_path in glob(os.path.join(input_dir, "**/*"), recursive=True):
        exif = _get_exif_data(image_path=image_path)
        assert isinstance(exif, dict)
        assert len(exif) > 0

        lat, lon = _extract_geolocation(image_path=image_path)
        assert isinstance(lat, float) and isinstance(lon, float)
        assert lat != lon

        loc = _resolve_gps_to_place(lat=lat, lon=lon)
        assert isinstance(loc, str)
        assert len(loc) > 0

        date = _extract_date(image_path=image_path)
        assert isinstance(date, datetime)
