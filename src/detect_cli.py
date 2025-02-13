from pathlib import Path

import click
import pandas as pd
from PIL import Image
from shapely import Polygon, box, from_wkt
from tqdm import tqdm

from Predict import model

SUPPORTED_FILEFORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}


@click.command()
@click.argument('input_folder', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.argument('output_csv', type=click.Path(path_type=Path))
def images_to_csv(input_folder, output_csv):
    """
    Accepts a folder of images and outputs a CSV file with filenames and their sizes.
    """

    overview_df = pd.read_csv(input_folder / "buildings.csv")

    detections = list()

    for _, building in tqdm(overview_df.iterrows(), total=len(overview_df)):

        image_filepath = input_folder / building['filename']

        if image_filepath.suffix.lower() not in SUPPORTED_FILEFORMATS:
            continue

        building_polygon: Polygon = from_wkt(building['building_geometry_wkt'])

        image = Image.open(image_filepath)
        results = model(image, stream=True, conf=0.5)
        results = list(results)

        if len(results) < 1:
            continue

        result = results[0]
        detected_boxes = result.boxes

        for i, detected_box in enumerate(detected_boxes):

            confidence_value = detected_box.conf.tolist()[0]
            bx = detected_box.xyxy.flatten().tolist()
            detection_bbox = box(bx[0], bx[1], bx[2], bx[3])

            # Intersection over Union (IoU) 
            intersect = building_polygon.intersection(detection_bbox)
            union = building_polygon.union(detection_bbox)
            iou_value = intersect.area / union.area

            # Percentage of the box within the building's extent
            percentage_detection_within_building = intersect.area / detection_bbox.area

            detections.append({
                "building_id": building['building_id'],
                "detection_nr": i,
                "confidence": confidence_value,
                "iou": iou_value,
                "percentage_detection_within_building": percentage_detection_within_building,
                "detection_bbox": detection_bbox.wkt
            })

        detections_df = pd.DataFrame(detections)
        detections_df.to_csv(output_csv, index=False)


if __name__ == '__main__':
    images_to_csv()
