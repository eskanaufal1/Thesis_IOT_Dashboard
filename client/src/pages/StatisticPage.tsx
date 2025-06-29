import { useState, useEffect, useMemo, useCallback, memo, useRef } from "react";
import { Card, Button } from "../components/UI";
import { motion } from "framer-motion";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import type { ChartOptions, ChartData } from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const StatisticPage = () => {
  const [voltageData, setVoltageData] = useState<number[]>([]);
  const [currentData, setCurrentData] = useState<number[]>([]);
  const [powerData, setPowerData] = useState<number[]>([]);
  const [sensor1Data, setSensor1Data] = useState<number[]>([]);
  const [sensor2Data, setSensor2Data] = useState<number[]>([]);
  const [sensor3Data, setSensor3Data] = useState<number[]>([]);
  const [sensor4Data, setSensor4Data] = useState<number[]>([]);
  const [relayStatus, setRelayStatus] = useState([false, false, false, false]);
  const [selectedDevice, setSelectedDevice] = useState("device1");

  // Available devices for selection (memoized to prevent re-creation)
  const devices = useMemo(() => [
    { value: "device1", label: "Smart Home Controller" },
    { value: "device2", label: "Garden Irrigation System" },
    { value: "device3", label: "Warehouse Lighting" },
    { value: "device4", label: "Security Access Control" },
    { value: "device5", label: "HVAC Controller" },
  ], []);

  // Device selection handler (memoized)
  const handleDeviceChange = useCallback((value: string) => {
    setSelectedDevice(value);
  }, []);

  // Function to generate random data between a given min and max with 1 decimal precision
  const generateRandomData = useCallback((min: number, max: number): number => {
    const value = Math.random() * (max - min) + min;
    return Math.round(value * 10) / 10; // Ensure 1 decimal place precision
  }, []);

  // Debounced data update function to prevent excessive re-renders
  // Use flushSync to batch all state updates in a single render cycle
  const updateDataDebounced = useCallback(() => {
    // Generate all new data at once to minimize re-renders
    const newVoltage = generateRandomData(220, 240);
    const newCurrent = generateRandomData(5, 15);
    const newPower = generateRandomData(1000, 3000);
    const newSensor1 = generateRandomData(2, 8);
    const newSensor2 = generateRandomData(1, 6);
    const newSensor3 = generateRandomData(3, 9);
    const newSensor4 = generateRandomData(0.5, 4);

    // Use React 18's automatic batching for better performance
    // All these state updates will be batched automatically
    setVoltageData((prevData) => {
      const newData = [...prevData, newVoltage];
      return newData.length > 10 ? newData.slice(1) : newData;
    });

    setCurrentData((prevData) => {
      const newData = [...prevData, newCurrent];
      return newData.length > 10 ? newData.slice(1) : newData;
    });

    setPowerData((prevData) => {
      const newData = [...prevData, newPower];
      return newData.length > 10 ? newData.slice(1) : newData;
    });

    setSensor1Data((prevData) => {
      const newData = [...prevData, newSensor1];
      return newData.length > 10 ? newData.slice(1) : newData;
    });

    setSensor2Data((prevData) => {
      const newData = [...prevData, newSensor2];
      return newData.length > 10 ? newData.slice(1) : newData;
    });

    setSensor3Data((prevData) => {
      const newData = [...prevData, newSensor3];
      return newData.length > 10 ? newData.slice(1) : newData;
    });

    setSensor4Data((prevData) => {
      const newData = [...prevData, newSensor4];
      return newData.length > 10 ? newData.slice(1) : newData;
    });
  }, [generateRandomData]);

  // Function to toggle relay state (on/off) - memoized to prevent re-renders
  const toggleRelay = useCallback((index: number) => {
    setRelayStatus((prevState) => {
      const newRelayStatus = [...prevState];
      newRelayStatus[index] = !newRelayStatus[index];
      return newRelayStatus;
    });
  }, []);

  // Use effect to simulate real-time data updates with optimized batching
  useEffect(() => {
    const interval = setInterval(() => {
      updateDataDebounced();
    }, 1000); // Update every 2 seconds

    return () => clearInterval(interval); // Cleanup on component unmount
  }, [updateDataDebounced]);

  const StatCard = useMemo(() => ({ 
    title, 
    value, 
    unit = "", 
    color = "blue" 
  }: { 
    title: string; 
    value: number | string; 
    unit?: string;
    color?: string;
  }) => {
    // Ensure consistent formatting for numeric values
    const formattedValue = typeof value === 'number' ? value.toFixed(1) : value;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        whileHover={{ scale: 1.02 }}
      >
        <Card className="hover:shadow-lg transition-shadow duration-300">
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
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
        </Card>
      </motion.div>
    );
  }, []);

  // Enhanced Line Chart Component using Chart.js with advanced memo and optimization
  const EnhancedLineChart = memo(({ 
    data, 
    color, 
    title, 
    unit
  }: { 
    data: number[]; 
    color: string; 
    title: string; 
    unit: string;
  }) => {
    // Use ref to track previous data and prevent unnecessary re-renders
    const prevDataRef = useRef<number[]>([]);
    const [chartData, setChartData] = useState<ChartData<'line'>>({ 
      labels: [], 
      datasets: [] 
    });
    
    // Color mapping for different chart types (memoized)
    const colorMap = useMemo(() => ({
      blue: "#3B82F6",
      green: "#10B981", 
      red: "#EF4444",
      purple: "#8B5CF6",
      indigo: "#6366F1",
      pink: "#EC4899",
      teal: "#14B8A6"
    }), []);
    
    const getColor = useCallback((colorKey: string) => 
      colorMap[colorKey as keyof typeof colorMap] || "#3B82F6", [colorMap]);
    
    // Only update chart data if the actual data has changed
    useEffect(() => {
      // Compare with previous data to avoid unnecessary updates
      const dataChanged = data.length !== prevDataRef.current.length || 
                          data.some((value, index) => value !== prevDataRef.current[index]);
      
      if (dataChanged && data.length > 0) {
        const lastTenData = data.slice(-10);
        
        const newChartData = {
          labels: lastTenData.map((_, index) => `T${index + 1}`),
          datasets: [
            {
              label: title,
              data: lastTenData.map(value => Number(value.toFixed(1))),
              borderColor: getColor(color),
              backgroundColor: getColor(color) + '20', // Add transparency
              borderWidth: 2,
              fill: false,
              tension: 0.1,
              pointRadius: 0,
              pointHoverRadius: 4,
              pointBackgroundColor: getColor(color),
              pointBorderColor: '#fff',
              pointBorderWidth: 2,
            },
          ],
        };
        
        setChartData(newChartData);
        prevDataRef.current = [...data]; // Update the ref
      }
    }, [data, title, color, getColor]);

    // Chart.js options (memoized to prevent recreation)
    const options: ChartOptions<'line'> = useMemo(() => ({
      responsive: true,
      maintainAspectRatio: false,
      animation: false, // Disable animations to prevent re-renders
      interaction: {
        intersect: false,
        mode: 'index',
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          titleColor: '#374151',
          bodyColor: '#374151',
          borderColor: '#E5E7EB',
          borderWidth: 1,
          callbacks: {
            label: (context) => {
              const value = Number(context.parsed.y).toFixed(1);
              return `${title}: ${value} ${unit}`;
            },
          },
        },
      },
      scales: {
        x: {
          display: false,  // Hide x-axis completely
        },
        y: {
          display: false,  // Hide y-axis completely
        },
      },
    }), [title, unit]);
    
    if (data.length < 2) {
      return (
        <div className="h-48 flex items-center justify-center text-gray-400">
          <span>Loading chart data...</span>
        </div>
      );
    }
    
    const currentValue = data[data.length - 1] || 0;
    
    return (
      <motion.div 
        className="space-y-4"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        {/* Header with current value and legend */}
        <motion.div 
          className="flex items-center justify-between"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <motion.span 
            className="text-sm font-medium text-gray-700 dark:text-gray-300"
            key={currentValue}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            Current: {Number(currentValue).toFixed(1)} {unit}
          </motion.span>
          <div className="flex items-center space-x-2">
            <motion.div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: getColor(color) }}
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            />
            <span className="text-xs text-gray-500 dark:text-gray-400">{title}</span>
          </div>
        </motion.div>
        
        {/* Chart.js Line Chart */}
        <motion.div 
          className="h-40"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <Line data={chartData} options={options} />
        </motion.div>
        
        {/* Statistics */}
        <motion.div 
          className="flex justify-between text-xs text-gray-500 dark:text-gray-400"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <span>Data Points: {data.slice(-10).length}</span>
          <span>Live Updates Every 2s</span>
        </motion.div>
      </motion.div>
    );
  }, (prevProps, nextProps) => {
    // Custom comparison function for React.memo
    // Only re-render if data, color, title, or unit actually changed
    return prevProps.data.length === nextProps.data.length &&
           prevProps.data.every((value, index) => value === nextProps.data[index]) &&
           prevProps.color === nextProps.color &&
           prevProps.title === nextProps.title &&
           prevProps.unit === nextProps.unit;
  });
  
  // Set display name for debugging
  EnhancedLineChart.displayName = 'EnhancedLineChart';

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
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Statistics
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
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
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Device:
            </span>
            <select
              value={selectedDevice}
              onChange={(e) => handleDeviceChange(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
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

      {/* Main Sensors Statistics */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }}
      >
        {useMemo(() => (
          <StatCard
            title="Main Voltage Sensor"
            value={voltageData[voltageData.length - 1] || 0}
            unit="V"
            color="blue"
          />
        ), [voltageData])}
        {useMemo(() => (
          <StatCard
            title="Main Current Sensor"
            value={currentData[currentData.length - 1] || 0}
            unit="A"
            color="green"
          />
        ), [currentData])}
        {useMemo(() => (
          <StatCard
            title="Power"
            value={powerData[powerData.length - 1] || 0}
            unit="W"
            color="red"
          />
        ), [powerData])}
      </motion.div>

      {/* Relay Controls - Memoized to prevent unnecessary re-renders */}
      {useMemo(() => (
        <motion.div 
          className="mb-8"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <Card title="Relay Controls">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {relayStatus.map((status, index) => (
                <motion.div
                  key={index}
                  className="text-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Relay {index + 1}
                  </p>
                  <div className="mb-3">
                    <motion.div
                      className={`w-8 h-8 mx-auto rounded-full transition-all duration-300 ${
                        status
                          ? "bg-green-500 shadow-lg shadow-green-500/30"
                          : "bg-red-500"
                      }`}
                      animate={status ? { 
                        boxShadow: [
                          "0 0 0 0 rgba(34, 197, 94, 0.4)",
                          "0 0 0 10px rgba(34, 197, 94, 0)",
                          "0 0 0 0 rgba(34, 197, 94, 0)"
                        ]
                      } : {}}
                      transition={{ duration: 1.5, repeat: status ? Infinity : 0 }}
                    />
                  </div>
                  <motion.p 
                    className={`text-sm font-semibold mb-3 transition-colors duration-200 ${
                      status ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
                    }`}
                    key={status ? "ON" : "OFF"}
                    initial={{ scale: 0.8 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.2 }}
                  >
                    {status ? "ON" : "OFF"}
                  </motion.p>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Button
                      onClick={() => toggleRelay(index)}
                      variant={status ? "danger" : "primary"}
                      size="sm"
                      className="w-full"
                    >
                      {status ? "Turn OFF" : "Turn ON"}
                    </Button>
                  </motion.div>
                </motion.div>
              ))}
            </div>
          </Card>
        </motion.div>
      ), [relayStatus, toggleRelay])}

      {/* Main Sensor Charts */}
      <motion.div 
        className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
      >
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card title="Main Voltage Sensor Statistic">
            <div className="p-4">
              <EnhancedLineChart
                data={voltageData}
                color="blue"
                title="Voltage"
                unit="V"
              />
            </div>
          </Card>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card title="Main Current Sensor Statistic">
            <div className="p-4">
              <EnhancedLineChart
                data={currentData}
                color="green"
                title="Current"
                unit="A"
              />
            </div>
          </Card>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card title="Power Statistic">
            <div className="p-4">
              <EnhancedLineChart
                data={powerData}
                color="red"
                title="Power"
                unit="W"
              />
            </div>
          </Card>
        </motion.div>
      </motion.div>

      {/* Individual Current Sensor Charts */}
      <motion.div 
        className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          whileHover={{ scale: 1.02 }}
        >
          <Card title="Current Sensor 1 Statistics">
            <div className="p-3">
              <EnhancedLineChart
                data={sensor1Data}
                color="purple"
                title="Sensor 1"
                unit="A"
              />
            </div>
          </Card>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          whileHover={{ scale: 1.02 }}
        >
          <Card title="Current Sensor 2 Statistics">
            <div className="p-3">
              <EnhancedLineChart
                data={sensor2Data}
                color="indigo"
                title="Sensor 2"
                unit="A"
              />
            </div>
          </Card>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.3 }}
          whileHover={{ scale: 1.02 }}
        >
          <Card title="Current Sensor 3 Statistics">
            <div className="p-3">
              <EnhancedLineChart
                data={sensor3Data}
                color="pink"
                title="Sensor 3"
                unit="A"
              />
            </div>
          </Card>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.4 }}
          whileHover={{ scale: 1.02 }}
        >
          <Card title="Current Sensor 4 Statistics">
            <div className="p-3">
              <EnhancedLineChart
                data={sensor4Data}
                color="teal"
                title="Sensor 4"
                unit="A"
              />
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default StatisticPage;


