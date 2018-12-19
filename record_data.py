import time
from datetime import datetime
import bme680
import threading
from model import db, DHTRecord
from optparse import OptionParser

def add_parser_options(parser):
	parser.add_option('-p', action="store_true", default=False, help="print every record to STDOUT [default: %default]")
	parser.add_option('-t', action="store", type="int", default=15, help="time interval in minutes to request readout from sensor [default: %default]")
	return parser


class SensorDatabase(threading.Thread):
	def __init__(self, minutes_interval, print_to_stdout):
		self.minutes_interval = minutes_interval
		self.print_to_stdout = print_to_stdout
		threading.Thread.__init__(self)

	def record_to_database(self, data):
		humidity, temperature, datetime = data
		record = DHTRecord(humidity, temperature, datetime)
		db.session.add(record)
		db.session.commit()

	def run(self):

                sensor = bme680.BME680()
                sensor.set_humidity_oversample(bme680.OS_2X)
                sensor.set_pressure_oversample(bme680.OS_4X)
                sensor.set_temperature_oversample(bme680.OS_8X)
                sensor.set_filter(bme680.FILTER_SIZE_3)
                sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)
                sensor.set_temp_offset(-4.9)

		while True:
                        if sensor.get_sensor_data():
			        data = sensor.data.humidity, sensor.data.temperature, datetime.now()
			        self.record_to_database(data)
			        if self.print_to_stdout:
				        print data
			time.sleep(self.minutes_interval * 60)

if __name__ == "__main__":
	parser = OptionParser()
	praser = add_parser_options(parser)
	opts, args = parser.parse_args()
	sd = SensorDatabase(opts.t, opts.p)
	sd.run()
