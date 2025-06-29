import { useState } from "react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card } from "../components/ui/card";
import { Modal } from "../components/ui/modal";
import {
  WifiIcon,
  ExclamationIcon,
  CheckCircleIcon,
  XCircleIcon,
  EditIcon,
  DeleteIcon,
  PlusIcon,
} from "../components/Icons";

interface Device {
  key: string;
  deviceName: string;
  status: string;
  location: string;
  relay1: string;
  relay2: string;
  relay3: string;
  relay4: string;
  lastSeen: string;
}

const DevicePage = () => {
  const [isAddDeviceModalOpen, setIsAddDeviceModalOpen] = useState(false);
  const [isEditDeviceModalOpen, setIsEditDeviceModalOpen] = useState(false);
  const [devices, setDevices] = useState<Device[]>([
    {
      key: "1",
      deviceName: "Device Name 1",
      status: "Online",
      location: "Living Room",
      relay1: "On",
      relay2: "Off",
      relay3: "On",
      relay4: "Off",
      lastSeen: "13/06/2025, 03:10:09",
    },
    {
      key: "2",
      deviceName: "Device Name 2",
      status: "Online",
      location: "Bedroom",
      relay1: "Off",
      relay2: "On",
      relay3: "Off",
      relay4: "On",
      lastSeen: "13/06/2025, 01:10:08",
    },
  ]);

  const [newDevice, setNewDevice] = useState({
    deviceName: "",
    status: "Offline",
    location: "",
    relay1: "Off",
    relay2: "Off",
    relay3: "Off",
    relay4: "Off",
  });

  const [editDevice, setEditDevice] = useState<Partial<Device>>({});

  const handleAddDeviceOk = () => {
    setDevices([
      ...devices,
      {
        key: (devices.length + 1).toString(),
        ...newDevice,
        lastSeen: new Date().toLocaleString(),
      },
    ]);
    setNewDevice({
      deviceName: "",
      status: "Offline",
      location: "",
      relay1: "Off",
      relay2: "Off",
      relay3: "Off",
      relay4: "Off",
    });
    setIsAddDeviceModalOpen(false);
  };

  const handleEditDeviceOk = () => {
    const updatedDevices = devices.map((device) =>
      device.key === editDevice.key ? { ...device, ...editDevice } : device
    );
    setDevices(updatedDevices);
    setIsEditDeviceModalOpen(false);
  };

  const handleDeleteDevice = (key: string) => {
    setDevices(devices.filter((device) => device.key !== key));
  };

  const handleRelayChange = (value: string, relay: string) => {
    setEditDevice((prevDevice) => ({
      ...prevDevice,
      [relay]: value,
    }));
  };

  const StatusIcon = ({ status }: { status: string }) => {
    if (status === "Online") {
      return <WifiIcon className="text-green-500" size={20} />;
    }
    return <ExclamationIcon className="text-red-500" size={20} />;
  };

  const RelayStatus = ({ status }: { status: string }) => {
    if (status === "On") {
      return <CheckCircleIcon className="text-blue-500" size={24} />;
    }
    return <XCircleIcon className="text-red-500" size={24} />;
  };

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">
          Devices
        </h1>
        <Button
          onClick={() => setIsAddDeviceModalOpen(true)}
          className="flex items-center space-x-2"
        >
          <PlusIcon size={16} />
          <span>Add Device</span>
        </Button>
      </div>

      {/* Device Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {devices.map((device, index) => (
          <div
            key={device.key}
            className="animate-fade-in"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <Card className="hover:shadow-lg transition-shadow duration-300">
              <div className="p-6">
                {/* Card Header */}
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
                    {device.deviceName}
                  </h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setEditDevice(device);
                        setIsEditDeviceModalOpen(true);
                      }}
                      className="p-2 text-slate-500 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors duration-200"
                    >
                      <EditIcon size={16} />
                    </button>
                    <button
                      onClick={() => handleDeleteDevice(device.key)}
                      className="p-2 text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors duration-200"
                    >
                      <DeleteIcon size={16} />
                    </button>
                  </div>
                </div>

                {/* Card Content */}
                <div className="space-y-4">
                  {/* Status */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                      Status
                    </span>
                    <div className="flex items-center space-x-2">
                      <StatusIcon status={device.status} />
                      <span
                        className={`font-medium ${
                          device.status === "Online"
                            ? "text-green-600 dark:text-green-400"
                            : "text-red-600 dark:text-red-400"
                        }`}
                      >
                        {device.status}
                      </span>
                    </div>
                  </div>

                  {/* Location */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                      Location
                    </span>
                    <span className="text-sm text-slate-900 dark:text-slate-50">
                      {device.location}
                    </span>
                  </div>

                  {/* Last Seen */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                      Last Seen
                    </span>
                    <span className="text-sm text-slate-900 dark:text-slate-50">
                      {device.lastSeen}
                    </span>
                  </div>

                  {/* Relays */}
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                    {[1, 2, 3, 4].map((relayNum) => (
                      <div
                        key={relayNum}
                        className="flex flex-col items-center space-y-2"
                      >
                        <div className="text-sm font-medium text-slate-700 dark:text-slate-300">
                          Relay {relayNum}
                        </div>
                        <RelayStatus
                          status={
                            device[`relay${relayNum}` as keyof Device] as string
                          }
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          </div>
        ))}
      </div>

      {/* Add Device Modal */}
      <Modal
        isOpen={isAddDeviceModalOpen}
        onClose={() => setIsAddDeviceModalOpen(false)}
        title="Add New Device"
        footer={
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => setIsAddDeviceModalOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleAddDeviceOk}>Add Device</Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Input
            placeholder="Device Name"
            value={newDevice.deviceName}
            onChange={(e) =>
              setNewDevice({ ...newDevice, deviceName: e.target.value })
            }
          />
          <Input
            placeholder="Location"
            value={newDevice.location}
            onChange={(e) =>
              setNewDevice({ ...newDevice, location: e.target.value })
            }
          />
          <select
            value={newDevice.status}
            onChange={(e) =>
              setNewDevice({ ...newDevice, status: e.target.value })
            }
            className="flex h-10 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-800 dark:bg-slate-950 dark:ring-offset-slate-950 dark:placeholder:text-slate-400 dark:focus-visible:ring-slate-300"
          >
            <option value="Offline">Offline</option>
            <option value="Online">Online</option>
          </select>
          {[1, 2, 3, 4].map((relayNum) => (
            <select
              key={relayNum}
              value={newDevice[`relay${relayNum}` as keyof typeof newDevice]}
              onChange={(e) =>
                setNewDevice({
                  ...newDevice,
                  [`relay${relayNum}`]: e.target.value,
                })
              }
              className="flex h-10 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-800 dark:bg-slate-950 dark:ring-offset-slate-950 dark:placeholder:text-slate-400 dark:focus-visible:ring-slate-300"
            >
              <option value="Off">Relay {relayNum} - Off</option>
              <option value="On">Relay {relayNum} - On</option>
            </select>
          ))}
        </div>
      </Modal>

      {/* Edit Device Modal */}
      <Modal
        isOpen={isEditDeviceModalOpen}
        onClose={() => setIsEditDeviceModalOpen(false)}
        title="Edit Device"
        footer={
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => setIsEditDeviceModalOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleEditDeviceOk}>Update Device</Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Input
            placeholder="Device Name"
            value={editDevice.deviceName || ""}
            onChange={(e) =>
              setEditDevice({ ...editDevice, deviceName: e.target.value })
            }
          />
          <Input
            placeholder="Location"
            value={editDevice.location || ""}
            onChange={(e) =>
              setEditDevice({ ...editDevice, location: e.target.value })
            }
          />
          <select
            value={editDevice.status || ""}
            onChange={(e) => handleRelayChange(e.target.value, "status")}
            className="flex h-10 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-800 dark:bg-slate-950 dark:ring-offset-slate-950 dark:placeholder:text-slate-400 dark:focus-visible:ring-slate-300"
          >
            <option value="Offline">Offline</option>
            <option value="Online">Online</option>
          </select>
          {[1, 2, 3, 4].map((relayNum) => (
            <select
              key={relayNum}
              value={editDevice[`relay${relayNum}` as keyof Device] || ""}
              onChange={(e) =>
                handleRelayChange(e.target.value, `relay${relayNum}`)
              }
              className="flex h-10 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-800 dark:bg-slate-950 dark:ring-offset-slate-950 dark:placeholder:text-slate-400 dark:focus-visible:ring-slate-300"
            >
              <option value="Off">Relay {relayNum} - Off</option>
              <option value="On">Relay {relayNum} - On</option>
            </select>
          ))}
        </div>
      </Modal>
    </div>
  );
};

export default DevicePage;
