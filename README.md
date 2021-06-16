# IPX Port Error Collector

The IPX Port Error Collector is a data collection module that gathers port error counters and port status from a 3080IPX and NATX device in a SDVN network.

The data collection module has the below distinct abilities and features:

1. Collects input and output error counters per port
2. Computes the difference of errors between collections and store into _delta_ fields
3. Supports custom port ranges or explicit ports

## Minimum Requirements:

- inSITE Version 10.3 and service pack 6
- Python3.7 (_already installed on inSITE machine_)
- Python3 Requests library (_already installed on inSITE machine_)

## Installation:

Installation of the status monitoring module requires copying two scripts into the poller modules folder:

1. Copy __port_collector.py__ script to the poller python modules folder:
   ```
    cp scripts/port_collector.py /opt/evertz/insite/parasite/applications/pll-1/data/python/modules/
   ```

2. Restart the poller application

## Configuration:

To configure a poller to use the module start a new python poller configuration outlined below

1. Click the create a custom poller from the poller application settings page
2. Enter a Name, Summary and Description information
3. Enter the host value in the _Hosts_ tab
4. From the _Input_ tab change the _Type_ to __Python__
5. From the _Input_ tab change the _Metric Set Name_ field to __ipx__
6. Select the _Script_ tab, then paste the contents of __scripts/poller_config.py__ into the script panel.

7. Locate the below section of the script for custom modifcations:
   ```
        params = {"address": host, "ports": [1, 3, "5 - 9", 11, 15, "20 - 23"], "type": "NATX"}
   ```
   
   Update the ports list with the ports that are needed to be collected.  A range of ports can be specified like such: "1 - 128"

   Update the "type" argument with a value of "NATX" or "IPX" for the type of device being collected.

8.  Save changes, then restart the poller program.

## Testing:

The process_monitor script can be ran manually from the shell using the following command
```
python port_collector.py
```

Below is the sample json file created:

```
{
 "l_input_errors": 0,
 "as_id": [
  "926.22@i",
  "931.22@i",
  "344.22@s",
  "921.22@i"
 ],
 "i_port": 23,
 "l_output_errors": 0,
 "s_label": "23",
 "s_operation_status": "DOWN",
 "l_input_errors_delta": 0,
 "l_output_errors_delta": 0
}
```