Controller Tuning Observations

The proportional gain (kp) significantly affected the robot's tracking performance. When a small kp value was used, the robot turned slowly toward the target and responded smoothly, but alignment took longer. With a moderate kp value, the robot tracked the object accurately and maintained stable motion. When a large kp value was selected, the robot reacted aggressively, causing oscillations and frequent left-right corrections. Therefore, a moderate kp value provided the best balance between responsiveness and stability.

Color Segmentation Observations

Color segmentation performance depended on the selected HSV threshold values. Properly tuned thresholds allowed reliable detection of the target object and accurate centroid estimation. Narrow threshold ranges sometimes failed to detect the object under varying lighting conditions, while wider ranges increased noise and caused false detections. The HSV color space proved effective for isolating colored objects and simplifying image processing.
