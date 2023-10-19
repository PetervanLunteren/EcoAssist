# This python file contains no code and is purely ment to provide more flexability
# for advanced EcoAssist / MegaDetector users. The parameter assigned here will be
# imported to classify_detectios.py and used for the result smoothening process.
# The parameters are initially set to a default value, but finetune them for the 
# best results for your ecosystem and animals. 

#############################
## CLASSIFICATION SMOOTHING #
#############################
## Only count detections with a classification confidence threshold above
## *classification_confidence_threshold*, which in practice means we're only
## looking at one category per detection.
##
## If an image has at least *min_detections_above_threshold* such detections
## in the most common category, and no more than *max_detections_secondary_class*
## in the second-most-common category, flip all detections to the most common
## category.
##
## Optionally treat some classes as particularly unreliable, typically used to overwrite an 
## "other" class.
##

# Here you can provide which categories are "other" classes, meaning classes where uncommon species 
# are lumped together. If you leave this uncommented, the script will assume you have a class called
# 'other' and use that. If it can't find 'other' in your classes, it will just skip the 'other'
# smoothing, but proceed with the ususal classification and sequence smoothing.

# other_category_names = ["Other", "Unknown"] # an example

# These are the opposite classes of 'other'. Which classes do you want smooth to from 'other'?
# If you leave this uncommented, the script will use all classes except 'other'. If it can't 
# find 'other' in your classes, it will just skip the 'other' smoothing, but proceed with the 
# ususal classification and sequence smoothing.

# non_other_category_names = ["lion", "elephant", "zebra"] # an example

# How many detections do we need above the classification threshold to determine a dominant category
# for an image?
min_detections_above_threshold = 4 # default is 4

# Even if we have a dominant class, if a non-dominant class has at least this many classifications
# in an image, leave them alone.
max_detections_secondary_class = 3 # default is 3

# If the dominant class has at least this many classifications, overwrite "other" classifications
min_detections_to_overwrite_other = 2 # default is 2

# What is the label for 'other' classifications?
# other_category = "other" DEBUG

# What confidence threshold should we use for assessing the dominant category in an image?
classification_confidence_threshold = 0.6 # default is 0.6

# Which classifications should we even bother over-writing?
classification_overwrite_threshold = 0.3 # default is 0.3

# Detection confidence threshold for things we count when determining a dominant class
detection_confidence_threshold = 0.2 # default is 0.2

# Which detections should we even bother over-writing?
detection_overwrite_threshold = 0.05 # default is 0.05


#######################
## SEQUENCE SMOOTHING #
#######################
## Here classifications will be smoothened based on image sequences. An image sequence is a burst
## of images with consequtive timestamps and equal location.

# Only switch classifications to the dominant class if we see the dominant class at least
# this many times
min_dominant_class_classifications_above_threshold_for_class_smoothing = 5 # default is 5

# If we see more than this many of a class that are above threshold, don't switch those
# classifications to the dominant class.
max_secondary_class_classifications_above_threshold_for_class_smoothing = 5 # default is 5

# If the ratio between a dominant class and a secondary class count is greater than this, 
# regardless of the secondary class count, switch those classificaitons (i.e., ignore
# max_secondary_class_classifications_above_threshold_for_class_smoothing).
#
# This may be different for different dominant classes, e.g. if we see lots of cows, they really
# tend to be cows. Less so for canids, so we set a higher "override ratio" for canids.
# Format as dictionary -> classification_categories_id : value
# To give a value for the rest of the categories, use None. 
# For example:   {"1" : 3, "2" : 6, None : 3}
min_dominant_class_ratio_for_secondary_override_table = {None : 3}

# If there are at least this many classifications for the dominant class in a sequence,
# regardless of what that class is, convert all 'other' classifications (regardless of 
# confidence) to that class.
min_dominant_class_classifications_above_threshold_for_other_smoothing = 3 # default is 3

# If there are at least this many classifications for the dominant class in a sequence,
# regardless of what that class is, classify all previously-unclassified detections
# as that class.
min_dominant_class_classifications_above_threshold_for_unclassified_smoothing = 3 # default is 3

# Only count classifications above this confidence level when determining the dominant
# class, and when deciding whether to switch other classifications.
classification_confidence_threshold = 0.6 # default is 0.6

# Confidence values to use when we change a detection's classification (the
# original confidence value is irrelevant at that point)
flipped_other_confidence_value = 0.6 # default is 0.6
flipped_class_confidence_value = 0.6 # default is 0.6
flipped_unclassified_confidence_value = 0.6 # default is 0.6
min_detection_confidence_for_unclassified_flipping = 0.15 # default is 0.15

