import math
import numpy as np


class EuclideanDistTracker:
    def __init__(self, roixy):
        # Bildausschnitt
        self.roixy = roixy
        
        # Store the center positions of the objects
        self.center_points = {}
        # Keep the count of the IDs
        # each time a new object id detected, the count will increase by one
        self.id_count = 0
        
        # Temp counter  (will be reseted after sending)
        # Index 0 -> Drivingdirection left
        # Index 1 -> Drivingdirection right
        self.counter = np.array([0,0])
        
        # Counter over all
        self.counter_all = np.array([0,0])
        
        self.detections = []
        
    def resetCounter(self):
        self.counter = np.array([0,0])
        
    def update(self):
        # Objects boxes and ids
        objects_bbs_ids = []

        # Get center point of new object
        # for rect in objects_rect:
        for rect in self.detections:
            x, y, w, h = rect
            cx = rect[0] + rect[2] // 2 
            cy = rect[1] + rect[3] // 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 75:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True

                    xlinie = ((self.roixy[1]-self.roixy[0])/2)
                    if cx - xlinie <= 0 and pt[0] - xlinie > 0:
                        self.counter[0] += 1
                        print("Counter: " +str(self.counter))
                    elif cx - xlinie >= 0 and pt[0] - xlinie < 0:
                        self.counter[1] += 1
                        print("Counter: " +str(self.counter))
                
                    break

            # New object is detected we assign the ID to that object
            if same_object_detected is False:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        # Clean the dictionary by center points to remove IDS not used anymore
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        # Update dictionary with IDs not used removed
        self.center_points = new_center_points.copy()
        
        # At the end, reset detections
        self.detections = []
        return objects_bbs_ids