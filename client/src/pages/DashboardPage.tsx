import React from "react";
import { Card } from "../components/UI";
import { WifiIcon, ExclamationIcon } from "../components/Icons";

const DashboardPage = () => {
  // Dummy Data
  const totalDevices = 5;
  const onlineDevices = 4;
  const offlineDevices = 1;
  const maintenanceDevices = 0;

  // Dummy relay data with device names
  const relayData = [
    {
      key: "1",
      deviceName: "Smart Home Controller",
      relay1: "On",
      relay2: "Off",
      relay3: "On",
      relay4: "Off",
      timestamp: "13/06/2025, 03:10:09",
    },
    {
      key: "2",
      deviceName: "Garden Irrigation System",
      relay1: "Off",
      relay2: "On",
      relay3: "Off",
      relay4: "On",
      timestamp: "13/06/2025, 01:10:08",
    },
    {
      key: "3",
      deviceName: "Warehouse Lighting",
      relay1: "On",
      relay2: "On",
      relay3: "Off",
      relay4: "Off",
      timestamp: "12/06/2025, 21:10:09",
    },
    {
      key: "4",
      deviceName: "Security Access Control",
      relay1: "Off",
      relay2: "Off",
      relay3: "On",
      relay4: "On",
      timestamp: "12/06/2025, 19:15:02",
    },
    {
      key: "5",
      deviceName: "HVAC Controller",
      relay1: "On",
      relay2: "Off",
      relay3: "On",
      relay4: "On",
      timestamp: "12/06/2025, 17:30:15",
    },
  ];

  const StatCard = ({ 
    title, 
    value, 
    icon, 
    color = "blue" 
  }: { 
    title: string; 
    value: number; 
    icon: React.ReactNode; 
    color?: string;
  }) => (
    <Card className="hover:shadow-lg transition-shadow duration-300 h-full">
      <div className="flex items-center h-full">
        <div className={`p-3 rounded-full bg-${color}-100 dark:bg-${color}-900/20 flex-shrink-0`}>
          {icon}
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
            {title}
          </p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {value}
          </p>
        </div>
      </div>
    </Card>
  );

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Welcome to your IoT Device Management Dashboard
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="animate-fade-in h-32" style={{ animationDelay: "0.1s" }}>
          <StatCard
            title="Total Devices"
            value={totalDevices}
            icon={<WifiIcon className="text-blue-600" size={24} />}
            color="blue"
          />
        </div>
        <div className="animate-fade-in h-32" style={{ animationDelay: "0.2s" }}>
          <StatCard
            title="Online Devices"
            value={onlineDevices}
            icon={<WifiIcon className="text-green-600" size={24} />}
            color="green"
          />
        </div>
        <div className="animate-fade-in h-32" style={{ animationDelay: "0.3s" }}>
          <StatCard
            title="Offline Devices"
            value={offlineDevices}
            icon={<ExclamationIcon className="text-red-600" size={24} />}
            color="red"
          />
        </div>
        <div className="animate-fade-in h-32" style={{ animationDelay: "0.4s" }}>
          <StatCard
            title="Maintenance"
            value={maintenanceDevices}
            icon={<ExclamationIcon className="text-yellow-600" size={24} />}
            color="yellow"
          />
        </div>
      </div>

      {/* Recent Relay Activity */}
      <div className="animate-fade-in" style={{ animationDelay: "0.5s" }}>
        <Card title="Recent Relay Activity">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Device Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Relay 1
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Relay 2
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Relay 3
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Relay 4
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {relayData.map((row) => (
                  <tr
                    key={row.key}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {row.deviceName}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {row.timestamp}
                    </td>
                    {[row.relay1, row.relay2, row.relay3, row.relay4].map((status, idx) => (
                      <td key={idx} className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            status === "On"
                              ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
                              : "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
                          }`}
                        >
                          {status}
                        </span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;

