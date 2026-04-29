import numpy as np

def get_zones(frame_width: int, frame_height: int):
    """
    Returns a dictionary of zone polygons as numpy arrays.
    Entrance: Left half of the frame
    Aisle: Right half of the frame
    """
    entrance_polygon = np.array([
        [0, 0],
        [frame_width // 2, 0],
        [frame_width // 2, frame_height],
        [0, frame_height]
    ])
    
    aisle_polygon = np.array([
        [frame_width // 2, 0],
        [frame_width, 0],
        [frame_width, frame_height],
        [frame_width // 2, frame_height]
    ])
    
    return {
        "entrance": entrance_polygon,
        "aisle": aisle_polygon
    }

if __name__ == "__main__":
    zones = get_zones(1920, 1080)
    print("Zones for 1920x1080:", zones)
