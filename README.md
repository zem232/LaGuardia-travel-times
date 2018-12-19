# Evaluation of LaGuardia Air Train Proposal Re: Travel Times
Evaluation of current travel times to LaGuardia Airport to compare with anticipated travel times with the proposed Air Train solution.
### Order to run notebooks:
<br/>
 
#### Download MTA Bus & Subway Data with API key
get_mta_data

#### Extract relevant information, organize into CSV files, produce frequency/wait distribution plots:
Python scripts used to clean bus data once downloaded are in the data-downloads folder:
<br/>
all notebooks which reference 'get_bus_info_2.py', for example get_bus_Q70
<br/>
Python scripts to organize subway data:
<br/>
plot_delays_script_all_in_one.ipynb
 <br/>
get_travel_times_script.ipynb
<br/>
merge_subway_gaps (if you want to merge different days of downloads to run the model)
<br/>
all the 'travel_times.py' files
<br/>
bus_waits_andplots.py
#### Running the Model

models_all_testing.ipynb
<br/>
