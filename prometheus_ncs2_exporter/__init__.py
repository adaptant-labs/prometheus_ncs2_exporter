import prometheus_client
import os
import usb.core
import threading
from argparse import HelpFormatter
from prometheus_client.core import GaugeMetricFamily
from openvino.inference_engine import IECore
from time import sleep


class NCS2DeviceExporter(object):
    def __init__(self, inference_engine=IECore(), device='MYRIAD', registry=prometheus_client.REGISTRY, model=None,
                 ip='0.0.0.0', port=8085, polling_interval=5, separate_thread=True):
        self.device = device
        self.ip = ip
        self.port = port
        self.polling_interval = polling_interval

        self._inference_engine = inference_engine
        self._separate_thread = separate_thread

        _supported_metrics = self._inference_engine.get_metric(self.device, 'SUPPORTED_METRICS')

        self._thermal_metric_support = 'DEVICE_THERMAL' in _supported_metrics
        if self._thermal_metric_support is False:
            print('\'DEVICE_THERMAL\' metric not supported on \'{}\''.format(device))

        registry.register(self)
        self.registry = registry

        if model is not None:
            self.exec_net = self.load_model(model)
        else:
            self.exec_net = None

        if separate_thread is True:
            self.thread = threading.Thread(target=self.run_http_server)
            self.thread.daemon = True
            self._shutdown_flag = threading.Event()

    def load_model(self, model):
        model_xml = model
        model_bin = os.path.splitext(model_xml)[0] + '.bin'

        net = self._inference_engine.read_network(model_xml, model_bin)
        return self._inference_engine.load_network(net, self.device)

    def get_temperature(self):
        if self._thermal_metric_support is False:
            return 0

        # Querying the DEVICE_THERMAL metric requires a valid network to be loaded, or it will throw a TypeError
        try:
            temperature = self._inference_engine.get_metric(self.device, 'DEVICE_THERMAL')
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
        if self._separate_thread is True:
            self.thread.start()

    def run_http_server(self):
        if self._separate_thread is False:
            return

        prometheus_client.start_http_server(addr=self.ip, port=self.port)

        while not self._shutdown_flag.isSet():
            sleep(self.polling_interval)

    def shutdown(self):
        if self._separate_thread is False:
            return

        self._shutdown_flag.set()
        self.thread.join()


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


class UsageFormatter(HelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=50):
        super().__init__(prog, indent_increment=indent_increment, max_help_position=max_help_position)
