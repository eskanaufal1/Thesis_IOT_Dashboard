import { useState, useEffect, useMemo, useCallback } from "react";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { motion } from "framer-motion";
import { AntiFlickerChart } from "../components/AntiFlickerChart";

// Enhanced dummy data generator with TradingView-like patterns
const generateDummyData = (
  baseValue: number,
  variance: number,
  trend: number = 0
) => {
  const time = Date.now();
  const noise = (Math.random() - 0.5) * variance;

  // Multiple overlapping sine waves for more realistic patterns
  const cyclicPattern1 = Math.sin(time / 10000) * (variance * 0.3);
  const cyclicPattern2 = Math.sin(time / 5000) * (variance * 0.15);
  const cyclicPattern3 = Math.sin(time / 20000) * (variance * 0.1);

  // Trend component with some randomness
  const trendComponent = (trend * (time % 100000)) / 100000;
  const trendNoise = (Math.random() - 0.5) * variance * 0.1;

  // Occasional spikes for realistic data
  const spike = Math.random() < 0.05 ? (Math.random() - 0.5) * variance * 2 : 0;

  const result =
    baseValue +
    noise +
    cyclicPattern1 +
    cyclicPattern2 +
    cyclicPattern3 +
    trendComponent +
    trendNoise +
    spike;

  return Math.max(0, result);
};

const StatisticPage = () => {
  // Store chart data in component state so React can track changes
  const [chartData, setChartData] = useState({
    voltage: Array.from({ length: 50 }, (_, i) => ({
      timestamp: Date.now() - (49 - i) * 1000,
      value: generateDummyData(230, 10, 0),
    })),
    current: Array.from({ length: 50 }, (_, i) => ({
      timestamp: Date.now() - (49 - i) * 1000,
      value: generateDummyData(10, 5, 0),
    })),
    power: Array.from({ length: 50 }, (_, i) => ({
      timestamp: Date.now() - (49 - i) * 1000,
      value: generateDummyData(2000, 500, 0),
    })),
    relay1: Array.from({ length: 50 }, (_, i) => ({
      timestamp: Date.now() - (49 - i) * 1000,
      value: generateDummyData(12, 3, 0.01),
    })),
    relay2: Array.from({ length: 50 }, (_, i) => ({
      timestamp: Date.now() - (49 - i) * 1000,
      value: generateDummyData(5, 1.5, -0.005),
    })),
    relay3: Array.from({ length: 50 }, (_, i) => ({
      timestamp: Date.now() - (49 - i) * 1000,
      value: generateDummyData(24, 4, 0.008),
    })),
    relay4: Array.from({ length: 50 }, (_, i) => ({
      timestamp: Date.now() - (49 - i) * 1000,
      value: generateDummyData(3.3, 0.8, 0.002),
    })),
  });

  // Simple state for current values display only
  const [currentValues, setCurrentValues] = useState({
    voltage: 230,
    current: 10,
    power: 2000,
    relay1: 12, // Relay 1 Voltage
    relay2: 5, // Relay 2 Voltage
    relay3: 24, // Relay 3 Voltage
    relay4: 3.3, // Relay 4 Voltage
  });
  const [relayStatus, setRelayStatus] = useState([false, false, false, false]);
  const [selectedDevice, setSelectedDevice] = useState("device1");

  // Available devices for selection (memoized to prevent re-creation)
  const devices = useMemo(
    () => [
      { value: "device1", label: "Smart Home Controller" },
      { value: "device2", label: "Garden Irrigation System" },
      { value: "device3", label: "Warehouse Lighting" },
      { value: "device4", label: "Security Access Control" },
      { value: "device5", label: "HVAC Controller" },
    ],
    []
  );

  // Device selection handler (memoized)
  const handleDeviceChange = useCallback((value: string) => {
    setSelectedDevice(value);
  }, []);

  // Debounced data update function for real-time updates
  const updateDataDebounced = useCallback(() => {
    const now = Date.now();

    // Generate new data points
    const newVoltage = { timestamp: now, value: generateDummyData(230, 10, 0) };
    const newCurrent = { timestamp: now, value: generateDummyData(10, 5, 0) };
    const newPower = { timestamp: now, value: generateDummyData(2000, 500, 0) };
    const newRelay1 = { timestamp: now, value: generateDummyData(12, 3, 0.01) }; // Relay 1: 12V
    const newRelay2 = {
      timestamp: now,
      value: generateDummyData(5, 1.5, -0.005),
    }; // Relay 2: 5V
    const newRelay3 = {
      timestamp: now,
      value: generateDummyData(24, 4, 0.008),
    }; // Relay 3: 24V
    const newRelay4 = {
      timestamp: now,
      value: generateDummyData(3.3, 0.8, 0.002),
    }; // Relay 4: 3.3V

    // Update chart data state (React will detect changes)
    setChartData((prevData) => ({
      voltage: [...prevData.voltage.slice(-49), newVoltage],
      current: [...prevData.current.slice(-49), newCurrent],
      power: [...prevData.power.slice(-49), newPower],
      relay1: [...prevData.relay1.slice(-49), newRelay1],
      relay2: [...prevData.relay2.slice(-49), newRelay2],
      relay3: [...prevData.relay3.slice(-49), newRelay3],
      relay4: [...prevData.relay4.slice(-49), newRelay4],
    }));

    // Update current values for display
    setCurrentValues({
      voltage: Number(newVoltage.value.toFixed(1)),
      current: Number(newCurrent.value.toFixed(1)),
      power: Number(newPower.value.toFixed(0)),
      relay1: Number(newRelay1.value.toFixed(1)),
      relay2: Number(newRelay2.value.toFixed(1)),
      relay3: Number(newRelay3.value.toFixed(1)),
      relay4: Number(newRelay4.value.toFixed(1)),
    });
  }, []);

  // Function to toggle relay state (on/off) - memoized to prevent re-renders
  const toggleRelay = useCallback((index: number) => {
    setRelayStatus((prevState) => {
      const newRelayStatus = [...prevState];
      newRelayStatus[index] = !newRelayStatus[index];
      return newRelayStatus;
    });
  }, []);

  // Use effect to simulate real-time data updates with TradingView-like frequency
  useEffect(() => {
    const interval = setInterval(() => {
      updateDataDebounced();
    }, 1000); // Update every 1 second for more dynamic feel

    return () => clearInterval(interval); // Cleanup on component unmount
  }, [updateDataDebounced]);

  const StatCard = useMemo(
    () =>
      ({
        title,
        value,
        unit = "",
        color = "blue",
      }: {
        title: string;
        value: number | string;
        unit?: string;
        color?: string;
      }) => {
        // Ensure consistent formatting for numeric values
        const formattedValue =
          typeof value === "number" ? value.toFixed(1) : value;

        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            whileHover={{ scale: 1.02 }}
          >
            <Card className="hover:shadow-lg transition-shadow duration-300">
              <div className="p-6">
                <div className="text-center">
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
                    {title}
                  </p>
                  <motion.p
                    className={`text-3xl font-bold text-${color}-600 dark:text-${color}-400 transition-all duration-200`}
                    key={formattedValue}
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                  >
                    {formattedValue}
                    <span className="text-lg ml-1">{unit}</span>
                  </motion.p>
                </div>
              </div>
            </Card>
          </motion.div>
        );
      },
    []
  );

  return (
    <motion.div
      className="min-h-screen"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <motion.div
        className="mb-6"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">
              Statistics
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-2">
              Real-time monitoring and control statistics
            </p>
          </motion.div>

          {/* Device Selection */}
          <motion.div
            className="flex items-center space-x-3"
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Device:
            </span>
            <select
              value={selectedDevice}
              onChange={(e) => handleDeviceChange(e.target.value)}
              className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
            >
              {devices.map((device) => (
                <option key={device.value} value={device.value}>
                  {device.label}
                </option>
              ))}
            </select>
          </motion.div>
        </div>
      </motion.div>

      {/* Main Statistics Display */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Voltage"
          value={currentValues.voltage}
          unit="V"
          color="blue"
        />
        <StatCard
          title="Current"
          value={currentValues.current}
          unit="A"
          color="green"
        />
        <StatCard
          title="Power"
          value={currentValues.power}
          unit="W"
          color="red"
        />
        <StatCard
          title="Device Status"
          value={selectedDevice === "device1" ? "Online" : "Offline"}
          color={selectedDevice === "device1" ? "green" : "red"}
        />
      </div>

      {/* Device Control Section */}
      <motion.div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
            Device Control
          </h2>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-slate-600 dark:text-slate-400">
              Real-time Control Active
            </span>
          </div>
        </div>

        {/* Relay Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {relayStatus.map((status, index) => (
            <motion.div
              key={index}
              className="bg-slate-50 dark:bg-slate-700 rounded-lg p-4 border-2 border-slate-200 dark:border-slate-600"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  Relay {index + 1}
                </span>
                <div
                  className={`w-3 h-3 rounded-full ${
                    status ? "bg-green-500" : "bg-slate-400"
                  }`}
                />
              </div>
              <Button
                onClick={() => toggleRelay(index)}
                variant={status ? "secondary" : "default"}
                size="sm"
                className={`w-full transition-all duration-200 border-2 ${
                  status
                    ? "border-slate-300 dark:border-slate-500 hover:border-slate-400 dark:hover:border-slate-400"
                    : "border-blue-500 dark:border-blue-400 hover:border-blue-600 dark:hover:border-blue-300"
                }`}
              >
                {status ? "Turn OFF" : "Turn ON"}
              </Button>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
                Status: {status ? "Active" : "Inactive"}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Real-time Charts Section - Bigger Charts Layout */}

      {/* Row 1: Voltage and Current Monitors */}
      <motion.div
        className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        {/* Voltage Chart */}
        <Card className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              Voltage Monitor
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Real-time voltage readings
            </p>
          </div>
          <AntiFlickerChart
            data={chartData.voltage}
            color="blue"
            title="Voltage"
            unit="V"
          />
        </Card>

        {/* Current Chart */}
        <Card className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              Current Monitor
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Real-time current flow
            </p>
          </div>
          <AntiFlickerChart
            data={chartData.current}
            color="green"
            title="Current"
            unit="A"
          />
        </Card>
      </motion.div>

      {/* Row 2: Power Monitor (Full Width) */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
      >
        <Card className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              Power Monitor
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Real-time power consumption
            </p>
          </div>
          <AntiFlickerChart
            data={chartData.power}
            color="red"
            title="Power"
            unit="W"
          />
        </Card>
      </motion.div>

      {/* Row 3: Relay 1 and Relay 2 */}
      <motion.div
        className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
      >
        <Card className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              Relay 1 Voltage
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              12V relay monitoring
            </p>
          </div>
          <AntiFlickerChart
            data={chartData.relay1}
            color="purple"
            title="Relay 1"
            unit="V"
          />
        </Card>

        <Card className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              Relay 2 Voltage
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              5V relay monitoring
            </p>
          </div>
          <AntiFlickerChart
            data={chartData.relay2}
            color="indigo"
            title="Relay 2"
            unit="V"
          />
        </Card>
      </motion.div>

      {/* Row 4: Relay 3 and Relay 4 */}
      <motion.div
        className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.9 }}
      >
        <Card className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              Relay 3 Voltage
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              24V relay monitoring
            </p>
          </div>
          <AntiFlickerChart
            data={chartData.relay3}
            color="pink"
            title="Relay 3"
            unit="V"
          />
        </Card>

        <Card className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              Relay 4 Voltage
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              3.3V relay monitoring
            </p>
          </div>
          <AntiFlickerChart
            data={chartData.relay4}
            color="teal"
            title="Relay 4"
            unit="V"
          />
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default StatisticPage;
