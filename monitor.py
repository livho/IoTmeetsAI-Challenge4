import time

from machine import I2C, Pin, UART

from lib import adafruit_am2320, adafruit_gps, sds011, adafruit_sgp30


def init_i2c(baudrate = 100000):
    """
    Initialize I2C bus
    :return:
    """
    i2c = I2C(0, I2C.MASTER)
    i2c.init(I2C.MASTER, baudrate=baudrate)

    return i2c


def get_temp_humidity():
    """
    Retrieve temperature (Celsius) and relative humidity form a pycom board,
    these sensors are a bit flakey, its ok if the readings fail
    :return: the temperature and the humidity
    """
    # init board params
    i2c = init_i2c(100000)
    am = adafruit_am2320.AM2320(i2c)

    # Number of reading tentatives, as this sensor does not always respond...
    n_try_max = 10

    success = False
    n_try = 0

    while not success and n_try < n_try_max:
        try:
            success = True
            return am.temperature, am.relative_humidity
        except Exception:
            n_try += 1

    return None


def get_gps():
    """
    Retrieve location data from a pycom board
    :return: x, y and z absolute coordinates
    """
    # Initialize UART
    uart = UART(1, baudrate=9600, timeout_chars=3000, pins=('P4', 'P3'))

    # Instanciate a Pin object linked to the enable pin of the GPS
    en_pin = Pin('P23', mode=Pin.OUT)

    # Instantiaite a GPS object
    gps = adafruit_gps.GPS(uart, en_pin)

    # Turns ON GPS (turn off using dps.disbale())
    gps.enable()

    # Turn on the basic GGA and RMC info (what you typically want)
    gps.send_command('PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

    # Set update rate to once a second (1hz).
    # gps.send_command('PMTK220,1000')
    # Set update rate to once every two second (0.5hz).
    gps.send_command('PMTK220,2000')
    # Set update rate to twice a second (2hz).
    # gps.send_command('PMTK220,500')

    # Make sure to call gps.update() as often as possible to prevent loss
    # of data.
    # This returns a bool that's true if it parsed new data.
    gps.update()
    if not gps.has_fix:
        # Try again if we don't have a fix yet.
        return None

    # We have a fix! (gps.has_fix is true)
    return gps.latitude, gps.longitude, gps.altitude_m


def get_pm10_pm25():
    """
    Retrieve dust measurements from a pycom board
    :return: the pm10 and pm25 measures
    """
    # Initialize UART pins(TX,RX)
    uart = UART(2, baudrate=9600, pins=('P21', 'P22'))

    # Instantiate a SDS011 object
    dust_sensor = sds011.SDS011(uart)

    # Instanciate a Pin object linked to the enable pin of the boost converter
    # (that supplies 5V to the SDS011)
    boost_en = Pin('P8', mode=Pin.OUT)

    # Stop fan
    dust_sensor.sleep()

    # Datasheet says to wait for at least 30 seconds.
    # Turns ON boost converter
    boost_en.value(1)
    # Turns on fan
    dust_sensor.wake()
    time.sleep(30)

    status = dust_sensor.read()
    pkt_status = dust_sensor.packet_status

    # Stop fan
    dust_sensor.sleep()

    if status == 'NOK':
        boost_en.value(0)  # Turns OFF boost converter
        return None
    elif pkt_status == 'NOK':
        boost_en.value(0)  # Turns OFF boost converter
        return None
    else:
        boost_en.value(0)  # Turns OFF boost converter
        return dust_sensor.pm10, dust_sensor.pm25


def co2_tvoc():
    """
    Retrieve CO2 and TVOC from a pycom board
    :return: the co2 and tvoc
    """
    i2c = init_i2c()

    # Create library object on our I2C port
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

    # Initialize SGP-30 internal drift compensation algorithm.
    sgp30.iaq_init()
    # Retrieve previously stored baselines, if any
    try:
        f_co2 = open('co2eq_baseline.txt', 'r')
        f_tvoc = open('tvoc_baseline.txt', 'r')

        co2_baseline = int(f_co2.read())
        tvoc_baseline = int(f_tvoc.read())
        # Use them to calibrate the sensor
        sgp30.set_iaq_baseline(co2_baseline, tvoc_baseline)

        f_co2.close()
        f_tvoc.close()
    except:
        pass

    # Store the time at which last baseline has been saved
    baseline_time = time.time()

    print('co2eq = ' + str(sgp30.co2eq) + ' ppm \t tvoc = ' + str(
        sgp30.tvoc) + ' ppb')

    # Baselines should be saved every hour, according to the doc.
    if (time.time() - baseline_time >= 3600):
        print('Saving baseline!')
        baseline_time = time.time()

        f_co2 = open('co2eq_baseline.txt', 'w')
        f_tvoc = open('tvoc_baseline.txt', 'w')

        f_co2.write(str(sgp30.baseline_co2eq))
        f_tvoc.write(str(sgp30.baseline_tvoc))

        f_co2.close()
        f_tvoc.close()
