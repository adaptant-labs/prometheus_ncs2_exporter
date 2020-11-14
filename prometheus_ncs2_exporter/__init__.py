import prometheus_client
import os
import usb.core
from prometheus_client.core import GaugeMetricFamily
from openvino.inference_engine import IECore


class NCS2DeviceExporter(object):
    def __init__(self, inference_engine=IECore(), device='MYRIAD', registry=prometheus_client.REGISTRY, model=None,
                 ip='0.0.0.0', port='8085', threading=False, polling_interval=5):
        self.device = device
        self.inference_engine = inference_engine
        self.ip = ip
        self.port = port
        self.threading = threading
        self.polling_interval = polling_interval

        _supported_metrics = self.inference_engine.get_metric(self.device, 'SUPPORTED_METRICS')

        self.thermal_metric_support = 'DEVICE_THERMAL' in _supported_metrics
        if self.thermal_metric_support is False:
            print('\'DEVICE_THERMAL\' metric not supported on \'{}\''.format(device))

        registry.register(self)
        self.registry = registry

        if model is not None:
            self.exec_net = self.load_model(model)
        else:
            self.exec_net = None

    def load_model(self, model):
        model_xml = model
        model_bin = os.path.splitext(model_xml)[0] + '.bin'

        net = self.inference_engine.read_network(model_xml, model_bin)
        return self.inference_engine.load_network(net, self.device)

    def get_temperature(self):
        if self.thermal_metric_support is False:
            return 0

        # Querying the DEVICE_THERMAL metric requires a valid network to be loaded, or it will throw a TypeError
        try:
            temperature = self.inference_engine.get_metric(self.device, 'DEVICE_THERMAL')
        except TypeError:
            # Return 0C if we're unable to obtain a reading
            return 0

        return temperature

    def collect(self):
        temp_gauge = GaugeMetricFamily('ncs2_temperature_celsius',
                                       'NCS2 device temperature in Celsius',
                                       labels=['name'])
        temp_gauge.add_metric(labels=[self.device], value=self.get_temperature())
        yield temp_gauge

    def start_http_server(self):
        pass


class NCS2Exporter(object):
    def __init__(self, registry=prometheus_client.REGISTRY):
        self.inference_engine = IECore()

        registry.register(self)
        self.registry = registry

    @staticmethod
    def num_devices():
        """ Scan for NCS2 devices """
        devs = usb.core.find(find_all=True, idVendor=0x3e7, idProduct=0x2485)
        if devs is None:
            raise ValueError('Unable to find any connected NCS2 devices')
        return len(list(devs))

    def num_available_devices(self):
        """ Find the number of available NCS2 devices """

        # A single device is expressed as 'MYRIAD', while multiple devices have a device number appended:
        # [ 'MYRIAD.0', 'MYRIAD.1', ... ]
        return sum(map(lambda x: 'MYRIAD' in x, self.inference_engine.available_devices))

    def get_available_devices(self):
        """ Obtain a list of available NCS2 devices """
        return [s for s in self.inference_engine.available_devices if 'MYRIAD' in s]

    def collect(self):
        yield GaugeMetricFamily('ncs2_num_devices', 'Number of NCS2 devices', value=self.num_devices())
        yield GaugeMetricFamily('ncs2_num_available_devices',
                                'Number of available NCS2 devices',
                                value=self.num_available_devices())
