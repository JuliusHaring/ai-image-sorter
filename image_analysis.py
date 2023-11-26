# image_analysis.py

import os
import exifread
import requests
import openai
from datetime import datetime
from glob import glob
import json


def get_exif_data(image_path):
    with open(image_path, "rb") as f:
        return exifread.process_file(f)


def get_decimal_from_dms(dms, ref):
    degrees = dms[0].num / dms[0].den
    minutes = dms[1].num / dms[1].den / 60.0
    seconds = dms[2].num / dms[2].den / 3600.0

    if ref in ["S", "W"]:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return degrees + minutes + seconds


def extract_geolocation(image_path):
    exif_data = get_exif_data(image_path)
    gps_latitude = exif_data.get("GPS GPSLatitude")
    gps_latitude_ref = exif_data.get("GPS GPSLatitudeRef")
    gps_longitude = exif_data.get("GPS GPSLongitude")
    gps_longitude_ref = exif_data.get("GPS GPSLongitudeRef")

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = get_decimal_from_dms(gps_latitude.values, gps_latitude_ref.values)
        lon = get_decimal_from_dms(gps_longitude.values, gps_longitude_ref.values)
        return (lat, lon)

    return None


def resolve_gps_to_place(lat, lon):
    response = requests.get(
        f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("display_name", "Unknown Location")
    return "Unknown Location"


def extract_date(image_path):
    exif_data = get_exif_data(image_path)
    date_taken = exif_data.get("EXIF DateTimeOriginal")
    if date_taken:
        return datetime.strptime(str(date_taken), "%Y:%m:%d %H:%M:%S")
    return None


def call_openai_for_analysis(
    api_key, image_info, folder_out, multiple_folders
) -> list[dict]:
    client = openai.OpenAI(api_key=api_key)

    system_prompt = """
    You are a program that gets as input images and data about them, such as Geolocations and Dates, and outputs where the files should be located.
    Always answer in JSON format, with the keys "input_image_path" and "output_image_path". Do just output a list of JSON which can be parsed in Python, nothing else.
    Hence, start with [ and end with ].
    If the Multiple folders allowed option is set to False, then only create a single folder for all files."""
    prompt = f"Image Info:\n{image_info}\nMultiple folders allowed: {multiple_folders}\nOutput folder:{folder_out}"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        json_result = response.choices[0].message.content.strip()
        return json.loads(json_result)

    except Exception as e:
        return f"Error in OpenAI response: {str(e)}"


def analyze_images_in_folder(
    api_key, folder_in: str, folder_out: str, multiple_folders: bool
) -> list[dict]:
    image_info = []
    for root, dirs, files in os.walk(folder_in):
        for file_pattern in [
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.tiff",
        ]:  # Add other relevant patterns
            for file_path in glob(os.path.join(root, file_pattern)):
                geo = extract_geolocation(file_path)
                place = resolve_gps_to_place(*geo) if geo else "Unknown"
                date = extract_date(file_path)
                image_info.append((file_path, place, date))

    # Add logic to check for output folders if required
    # ...

    folder_out_substructue = "\n".join(
        glob(os.path.join(folder_out, "**/*"), recursive=True)
    )
    return call_openai_for_analysis(
        api_key, image_info, folder_out_substructue, multiple_folders
    )


if __name__ == "__main__":
    folders = analyze_images_in_folder(
        os.environ["OPENAI_API_KEY"],
        "/Users/julius/projects/image-sorter/test_in",
        "/Users/julius/projects/image-sorter/test_out",
        True,
    )
    print(folders)
