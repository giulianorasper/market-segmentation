# FoundHere
This repository contains the source code and documentation for the market segmentation project as part of the Data Science lecture at Saarland University. The project focuses on developing a Monte Carlo-based market segmentation system for recommending locations to found specific companies. The system utilizes clustering algorithms to group companies based on their characteristics and provides location recommendations based on a set of defined criteria.

Here you can see a screenshot of the web application, making recommendations for founding an AI consultancy in Saarland, Germany.
![](pictures/saarlandRecommendations.png)

# Installation and Running
The project requires a python3 installation to work. Make
sure to create a new python environment before installing the requirements using:
```pip install -r requirements.txt```.

To run the project execute the following command:
```python3 main.py```.
By default the web application will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

Make sure that you have a stable internet connection when first running the program, as required models will not be downloaded otherwise.


# References
For more information on the project refer to the [project report](https://www.overleaf.com/read/bfbdckwcrppp).
Details about the algorithm extending standard monte carlo with MLPs can be found in the [paper](https://www.overleaf.com/read/wcqnzxdghjrq).