import argparse
import prometheus_client
from time import sleep
from . import NCS2Exporter, NCS2DeviceExporter, UsageFormatter


def main():
    parser = argparse.ArgumentParser(description='Prometheus Exporter for Intel NCS2 Metrics',
                                     formatter_class=UsageFormatter)
    parser.add_argument('--ip', dest='ip', help='IP address to bind to (default: %(default)s)',
                        default='0.0.0.0')
    parser.add_argument('--port', dest='port', help='Port to expose metrics on (default: %(default)s)',
                        type=int, default=8084)
    parser.add_argument('--polling-interval', dest='polling_interval', type=int, default=1, metavar='SEC',
                        help='Polling interval in seconds (default: %(default)s)')
    parser.add_argument('--model', dest='model', help='XML (IR) model to load (only for validation)')
    parser.add_argument('--instantiate-devices', action='store_true', dest='instantiate_devices',
                        help='Instantiate available devices (only for validation)')
    args = parser.parse_args()

    if args.model is not None:
        print('Loading Model: {}'.format(args.model))
        # Model loading implies device instantiation
        args.instantiate_devices = True

    # Initialize the main collector
    ncs2 = NCS2Exporter()

    if args.instantiate_devices is True:
        # Initialize per-device collectors, polling from the main thread
        for device_name in ncs2.get_available_devices():
            dev = NCS2DeviceExporter(device=device_name, inference_engine=ncs2.inference_engine,
                                     model=args.model, separate_thread=False)
            print('Gathering metrics from \'{}\' device'.format(dev.device))

    print('Listening on: {}:{}'.format(args.ip, args.port))
    prometheus_client.start_http_server(addr=args.ip, port=args.port)

    while True:
        sleep(args.polling_interval)


if __name__ == '__main__':
    main()
