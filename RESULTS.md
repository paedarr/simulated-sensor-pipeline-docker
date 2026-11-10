### Results of Server kill

on server.py, a CTRL+C interrupt was executed, stopping the server. `collector.py` was left running, resulting in these messages:

```
Requested session timeout to be 3600000ms, got 600000ms instead
connected to PLC
lost connection: client is disconnected; reconnecting
close_session was called but connection is closed
close_secure_channel was called but connection is closed
connect failed (); retrying in 1s
```

restarted `server.py`, and it connected with the following messages:

```
Requested session timeout to be 3600000ms, got 600000ms instead
connected to PLC
```

### Run database down test

Ran the command `docker compose stop influxdb`, to stop the influxdb, which resulted in `collector.py` printing:

```
The retriable error occurred during request. Reason: '('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))'.
The retriable error occurred during request. Reason: 'HTTPConnection(host='localhost', port=8086): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'.
The retriable error occurred during request. Reason: 'HTTPConnection(host='localhost', port=8086): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'.
```

Resumed using `docker compose start influxdb`. It seems like during downtime, there was some data aberration, as shown here:

![Downtime graph spike](images_md/downtime-data-aberration.png)

We can see that the following is true:
- chamber_pressure_psi (blue): ramps up, holds at 400, then drops sharply
- thrust_lbf (orange): follows the pressure curve at 80% of its height
- chamber_temp_k (purple): climbs toward about 1800 and levels off

This is all a result of the downtime in the influxdb.


### Running tests

Finally, I ran a `pytest` on the project to see if there were any issues, to which there were not. All 3 passed:

```
rootdir: <project location on my C drive, removing path for safety>
plugins: anyio-4.16.0
collected 3 items                                                                                                                                                                                                   

tests\test_signals.py ...                                                                                                                                                                                     [100%]

================================================================================================ 3 passed in 0.09s =================================================================================================
```

---

### Further Tests 11/9

##### Added more to `test_signals.py`, trying to get more familiar with InfluxDB and how all these pieces communicate with one another in this simulated PLC 


#### Results of new test:


```
py -m pytest -v
==================================================== test session starts ====================================================
platform win32 -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\paeda\Documents\GitHub\simulated-sensor-pipeline-docker\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\paeda\Documents\GitHub\simulated-sensor-pipeline-docker
plugins: anyio-4.16.0
collected 18 items                                                                                                           

tests/test_signals.py::test_pressure_ramps_up PASSED                                                                   [  5%]
tests/test_signals.py::test_pressure_holds_then_decays PASSED                                                          [ 11%]
tests/test_signals.py::test_all_channels_have_unique_names PASSED                                                      [ 16%]
tests/test_signals.py::test_pressure_never_negative PASSED                                                             [ 22%]
tests/test_signals.py::test_pressure_never_exceeds_peak PASSED                                                         [ 27%]
tests/test_signals.py::test_pressure_is_finite_everywhere PASSED                                                       [ 33%]
tests/test_signals.py::test_ramp_is_monotonic_non_decreasing PASSED                                                    [ 38%]
tests/test_signals.py::test_decay_is_monotonic_non_increasing PASSED                                                   [ 44%]
tests/test_signals.py::test_pressure_returns_float PASSED                                                              [ 50%]
tests/test_signals.py::test_pressure_is_repeatable PASSED                                                              [ 55%]
tests/test_signals.py::test_pressure_accepts_float_times[0.0] PASSED                                                   [ 61%]
tests/test_signals.py::test_pressure_accepts_float_times[1.0] PASSED                                                   [ 66%]
tests/test_signals.py::test_pressure_accepts_float_times[5.0] PASSED                                                   [ 72%]
tests/test_signals.py::test_pressure_accepts_float_times[10.0] PASSED                                                  [ 77%]
tests/test_signals.py::test_pressure_accepts_float_times[30.0] PASSED                                                  [ 83%]
tests/test_signals.py::test_channels_list_is_not_empty PASSED                                                          [ 88%]
tests/test_signals.py::test_channel_names_are_nonempty_strings PASSED                                                  [ 94%]
tests/test_signals.py::test_channel_names_have_no_spaces PASSED                                                        [100%]

==================================================== 18 passed in 0.08s =====================================================
(.venv) PS C:\Users\paeda\Documents\GitHub\simulated-sensor-pipeline-docker> 
```


After all the tests have successfully passed, I want to try and mess with `signals.py` a bit more, and get more familiar with InfluxDB. Also, understanding how the OPC UA works in `server.py` is also really important; so that's at the top of my to-do.


> this project is a simulated PLC data interface :: it uses the same OPC UA protocol a real controller uses, so the collector would work against a real device with only the endpoint and node names changed. there is no implementation of real control logic or scan cycles (maybe though, future work?)