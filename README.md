# plot_simply
Functions for quicker use of common plotting tools, especially involving geographic plots

### To build matching environment:

(1) Navigate to folder in terminal and run:
conda env create --file=environment.yml

(2) Optional: if running in Jupyter Notebook environment
After creating the environment, you will next need to add it to the list of available kernels. 
This does not happen automatically. In the command line, run:
python -m ipykernel install --user --name <NAME>
* Make sure to replace <NAME> with the name of the environment

If conda command not recognized by default with terminal launch:
source /opt/anaconda3/bin/activate

(3) Optional, to update environment file after modifying packages:
conda env export > environment.yml
