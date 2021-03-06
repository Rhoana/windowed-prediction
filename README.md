# Membrane and Synapse Detection
Convolutional network for membrane and synapse detection.

### Dependencies
* [Numpy](http://www.numpy.org)
* [Scipy](http://www.scipy.org)
* [Theano](http://www.deeplearning.net/software/theano/)
* [YAML](http://pyyaml.org)
* [PIL](http://www.pythonware.com/products/pil/)
* [Mahotas](http://mahotas.readthedocs.org/en/latest/)
* [Gala](https://pypi.python.org/pypi/gala/0.1.1)
* [Matplotlib](http://matplotlib.org) (for plotting)


### Install
Install and upgrade all dependencies:

`pip install -U numpy theano matplotlib pyyaml pil scipy mahotas gala`

Clone repository:

`git clone https://github.com/Rhoana/windowed-prediction.git`

### Run (default settings)
1. Place training data in `data`-folder. Data can be downloaded from [Google Drive](https://drive.google.com/drive/u/1/folders/0B016PpcCQHuVfmdYSEdxSGVHdDNuenJyQjdZdkRkUXVOamFzSEpua0hfSzNQX0xSLXpaMFU?ltmpl=drive).
2. Specify data-folders in `config/global.yaml`
3. Run default configuration: `python runner.py`
4. Plot latest run: `python plot.py`

### Documentation

Further documentation can be found [here](https://github.com/Rhoana/windowed-prediction/wiki) (under progress).

### Contact

Hallvard Moian Nydal - hallvardnydal@gmail.com



