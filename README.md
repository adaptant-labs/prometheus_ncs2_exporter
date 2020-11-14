# Intel NCS2 Prometheus Exporter

A Prometheus exporter for the Intel Neural Compute Stick 2 (NCS2) / Intel Movidius MyriadX

## Metrics

The following metrics are exported:

| Metric | Description |
|--------|-------------|
| ncs2_num_devices | The total number of NCS2 devices |
| ncs2_num_available_devices | The total number of *available* NCS2 devices |
| ncs2_temperature_celsius | NCS2 device temperature in Celsius (per device) |

Viewed from the exporter:

```
# TYPE ncs2_num_devices gauge
ncs2_num_devices 1.0
# HELP ncs2_num_available_devices Number of available NCS2 devices
# TYPE ncs2_num_available_devices gauge
ncs2_num_available_devices 1.0
# HELP ncs2_temperature_celsius NCS2 device temperature in Celsius
# TYPE ncs2_temperature_celsius gauge
ncs2_temperature_celsius{name="MYRIAD"} 40.917320251464844
```

**Note:** Unfortunately, as the current OpenVINO API does not presently permit querying the `DEVICE_THERMAL` metric
directly without a model loaded onto the device, the `ncs2_temperature_celsius` metric will, therefore, return 0°C for
devices that don't presently have a model loaded. Furthermore, applications that are using the NCS2 device directly
may result in the device being flagged as *unavailable* by the OpenVINO runtime, preventing the main exporter from
being able to enumerate the device or obtain metrics from it. In order to mitigate these issues, the exporter has been
split into two parts:

- The main exporter that provides an overview of NCS2 devices on the system (discoverable/available)
- A device metric exporter to be instantiated within each NCS2-enabled inference application independently

### Device Metric Exporter Instantiation in Inference Applications

#### Automated Metric Scraping / Kubernetes Pod Annotation

As each application instantiating the device metric exporter will be exposing metrics, Kubernetes Pods should be
annotated with the `prometheus.io/scrape: true` annotation in order to be automatically scraped alongside the main
exporter.

## Device Validation with Model Loading

The option to load a model onto each available device is provided for
validating the functionality of the exporter, but as this generates work on the device-under-monitoring and, worse,
potentially makes a device unavailable to a service that actually needs it, should never be used in production.

## Features and bugs

Please file feature requests and bugs in the [issue tracker][tracker].

## Acknowledgements

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant
agreement No 825480 ([SODALITE]).

## License

`ncs2-exporter` is licensed under the terms of the Apache 2.0 license, the full
version of which can be found in the LICENSE file included in the distribution.

[tracker]: https://github.com/adaptant-labs/ncs2-exporter/issues
[adaptant/ncs2-exporter]: https://hub.docker.com/repository/docker/adaptant/ncs2-exporter
[SODALITE]: https://sodalite.eu