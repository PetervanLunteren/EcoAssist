# Delegate the boring stuff to MegaDetector and EcoAssist
If you want to train your own species classifier and need to label animals, the steps below can save you many, many hours of boring work. It will use the awesome power of MegaDetector to automatically draw the bounding boxes on your images. You’ll only have to review them and adjust where necessary.

1. Collect all your images in one folder - the more the better. It doesn’t really matter if and how many empties there are. Just note that there should not be any subfolders or files other than images meant for training. It should look like the following.

```
	─── 📁dataset
	    |──image_1.jpg
	    |──image_2.jpg
	    |──image_3.jpg
	    :
	    └──image_N.jpg
```

2. Open EcoAssist and navigate to the ‘Deploy’ tab.

<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist-metadata/blob/main/imgs/figs-bonus-tip/deploy.png" width=100% height="auto" >
</p>

3. Select the folder with training data at ‘Step 1’.
4. Select one of the MegaDetector models at the ‘Model’ option. See the 'Help' tab for more info.
5. Select ‘Process all images in the folder specified’. If desired, specify checkpoint usage.
6. Click ‘Deploy model’ and wait for it to finish.

<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist-metadata/blob/main/imgs/figs-bonus-tip/post-process.png" width=100% height="auto" >
</p>

7. Choose a ‘Destination folder’ at ‘Step 3’.
8. Tick ‘Separate files into subdirectories’ and ‘Create annotations in YOLO format’.
9. Adjust the threshold if desired or just use the default value.
10. Click ‘Post-process files’. When the process has completed, you should have a subfolder called 'animal' containing images of animals and their label files. 

<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist-metadata/blob/main/imgs/figs-bonus-tip/annotate.png" width=100% height="auto" >
</p>

11. Navigate to the ‘Annotate’ tab.
12. Select the ‘animal’ subfolder inside the destination folder to annotate.
13. Provide the names of the species you are interested in as classes. Start with the species you expect to find most frequently.
14. Click ‘Start annotation’.
15. In the new window you can see that all detections that MegaDetector thought were animals are already boxed and have been given the label which you entered first at step 13. Now you just have to review them and adjust where necessary. I’d recommend to select ‘View’ > ‘Auto save mode’ from the menu bar for a quicker workflow.
16. When everything is reviewed and labelled, consider making the dataset open-source so that other ecologists can use it for their projects too. Dan Morris keeps an online database for datasets like these, called [LILA BC](https://lila.science/). If you’re interested in sharing, [e-mail him](mailto:info@lila.science).
17. It’s recommended to have about 0-10% images without your animal of interest in your final dataset to reduce false positives. Besides empty images, consider adding some images of vehicles, people and other animals – depending on what you expect to find when deploying the model. You want to create a dataset which resembles the true situation as much as possible and clarify that these images are not of interest.
18. Make sure you back up your data before you start training.
