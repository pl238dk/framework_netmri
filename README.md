# NetMRI Framework

This framework exists as a way to interact with the NetMRI API to retrieve data in an efficient manner. A few other methods of retrieving data have been tested without success, causing queries to exceed 2 hours per function-call.

The latest iteration of this framework is able to retrieve data in under 2 minutes for the average query for an entire API method's data. This is also done in a way that is gentle to the NetMRI back-end querying mechanism.

## Configuration of credential storage

API Credentials are structured in the same format as `configuration_template.json` and are to be placed in a file named `configuration.json`.

## Configuration of main object

Instantiate the NetMRI object by passing the NetMRI front-end configuration from `configuration.json` under the `config` parameter.

NetMRI servers are in the `configuration_template.json` file for each of the current respective servers.
```python
# NetMRI server
na = NetMRI('custom')

```

After the object has authenticated automatically to the NetMRI API, queries may be executed to an API service.

The most common API service for NetMRI is `infra_devices`, which holds the majority of the data retrieved by the NetMRI scanning mechanisms.

A query made to the network infrastructure service for a given hostname is structured as follows :
```python
parameters = {
  # A core switch in a made-up location
  'DeviceName': 'device123',
  # Only retrieve 1 device, in case duplicates exist
  'limit':  1,
}

# Query using the NetMRI server from above instantiation
results_alp = na.query(
  'infra_devices',
  params=parameters,
)
```

Results are stored in a format structured as follows :
```python
{
  # Boolean indicating whether or not the query was successful
  'success':  True,
  # Parsed and formatted data, converted from XML/JSON to be used by Python
  'result': result_data,
  # Requests object returned by the API query
  'response_object':  raw_response_object,
}
```
