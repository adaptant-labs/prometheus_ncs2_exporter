# Intel NCS2 Prometheus Exporter

A Prometheus exporter for the Intel Neural Compute Stick 2 (NCS2) / Intel Movidius MyriadX

## Usage

`prometheus_ncs2_exporter` can be run as-is without any additional configuration.

```
usage: prometheus_ncs2_exporter [-h] [--ip IP] [--port PORT]
                                [--polling-interval SEC] [--model MODEL]
                                [--instantiate-devices]

Prometheus Exporter for Intel NCS2 Metrics

optional arguments:
  -h, --help              show this help message and exit
  --ip IP                 IP address to bind to (default: 0.0.0.0)
  --port PORT             Port to expose metrics on (default: 8084)
  --polling-interval SEC  Polling interval in seconds (default: 1)
  --model MODEL           XML (IR) model to load (only for validation)
  --instantiate-devices   Instantiate available devices (only for validation)
```

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

A high-level overview of the expected interactions, metric sources, and integration points is as follows:

![NCS2 Exporter Overview](overview.png)

### Device Metric Exporter Instantiation in Inference Applications

#### Automated Metric Scraping / Kubernetes Pod Annotation

As each application instantiating the device metric exporter will be exposing metrics, Kubernetes Pods should be
annotated with the `prometheus.io/scrape: true` annotation in order to be automatically scraped alongside the main
exporter.

### Device Validation with Model Loading

The option to load a model onto each available device is provided for
validating the functionality of the exporter, but as this generates work on the device-under-monitoring and, worse,
potentially makes a device unavailable to a service that actually needs it, should never be used in production.

## Alerting Rules

The stated nominal operating range for the NCS2 is between 0°C and 40°C. While it can still operate at higher
temperatures, there is an increased risk of inference failures being produced. Thermal throttling is applied
automatically once the internal device temperature reaches 70°C, at which point the USB device will automatically
disconnect itself and it will no longer be possible to obtain thermal readings until it cools off and re-attaches.

With these points in mind, sample alerting rules for Prometheus (provided in [alerting_rules.yml](alerting_rules.yml)
for convenience) are as follows:

```yaml
groups:
  - name: ncs2_temp_monitoring
    rules:
      - alert: ncs2_temp_warning
        expr: ncs2_temperature_celsius > 45.0
        labels:
          severity: warning
        annotations:
          summary: "High NCS2 device temperature"
      - alert: ncs2_temp_critical
        expr: ncs2_temperature_celsius > 65.0
        labels:
          severity: critical
        annotations:
          summary: "Critical NCS2 device temperature"
```

Depending on the deployment, it may be necessary to increase the warning threshold to avoid spurious warnings. It is
recommended to monitor the expected upper bounds of the inference workload in real-world deployments and to adjust this
accordingly.

## Features and bugs

Please file feature requests and bugs in the [issue tracker][tracker].

## Acknowledgements

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant
agreement No 825480 ([SODALITE]).

## License

`prometheus_ncs2_exporter` is licensed under the terms of the Apache 2.0 license, the full
version of which can be found in the LICENSE file included in the distribution.

[tracker]: https://github.com/adaptant-labs/prometheus_ncs2_exporter/issues
[SODALITE]: https://sodalite.eu
