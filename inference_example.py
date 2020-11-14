import argparse
import os
import signal
from prometheus_ncs2_exporter import NCS2DeviceExporter, UsageFormatter
from openvino.inference_engine import IECore
from time import sleep


class AppShutdown(Exception):
    pass


def app_shutdown(signum, frame):
    print('Caught signal {}, exiting...'.format(signum))
    raise AppShutdown


def main():
    parser = argparse.ArgumentParser(description='Sample NCS2 inference application with integrated metric exporter',
                                     formatter_class=UsageFormatter)
    parser.add_argument('--device', dest='device', help='NCS2 device name (default: %(default)s)', default='MYRIAD')
    parser.add_argument('--model', dest='model', help='XML (IR) model to load', required=True)
    parser.add_argument('--metrics-port', dest='metrics_port', type=int, default=8085, metavar='PORT',
                        help='Port to expose device metrics on (default: %(default)s)')
    parser.add_argument('--polling-interval', dest='polling_interval', type=int, default=5, metavar='SEC',
                        help='Metric polling interval in seconds (default: %(default)s)')
    args = parser.parse_args()

    # Install signal handlers to clean up the metric exporter thread
    signal.signal(signal.SIGTERM, app_shutdown)
    signal.signal(signal.SIGINT, app_shutdown)

    inference_engine = IECore()

    model_xml = args.model
    model_bin = os.path.splitext(model_xml)[0] + '.bin'

    # Read the specified network
    net = inference_engine.read_network(model_xml, model_bin)
    print('Network: {}'.format(net.name))

    # Load the network onto the device
    print('Loading network onto {} device...'.format(args.device))
    exec_net = inference_engine.load_network(net, args.device)

    print('Running network: {}'.format(exec_net.get_metric('NETWORK_NAME')))

    # Initialize the device metric exporter
    exporter = NCS2DeviceExporter(inference_engine=inference_engine,
                                  polling_interval=args.polling_interval,
                                  port=args.metrics_port)

    print('Running in the main thread')

    try:
        while True:
            print('Sleeping in main thread...')
            sleep(5)
    except AppShutdown:
        exporter.shutdown()


if __name__ == '__main__':
    main()