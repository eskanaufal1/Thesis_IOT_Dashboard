import React, { useState, useEffect } from "react";
import {
  Button,
  Input,
  Modal,
  Select,
  Skeleton,
  notification,
  Row,
  Col,
  Card,
  Statistic,
  Typography,
  Layout,
} from "antd";
import {
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WifiOutlined,
  DisconnectOutlined,
  PlusOutlined, // Import PlusOutlined icon
} from "@ant-design/icons";
import apiClient from "../api"; // Import Axios instance

const { Title } = Typography;
const { Option } = Select;

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

const getInitialDeviceState = (): Device => ({
  key: "",
  deviceName: "",
  status: "Offline",
  location: "",
  relay1: "Off",
  relay2: "Off",
  relay3: "Off",
  relay4: "Off",
  lastSeen: new Date().toLocaleString(),
});

const DevicePage: React.FC = () => {
  const [isAddDeviceModalOpen, setIsAddDeviceModalOpen] = useState(false);
  const [isEditDeviceModalOpen, setIsEditDeviceModalOpen] = useState(false);
  const [devices, setDevices] = useState<Device[]>([]);
  const [newDevice, setNewDevice] = useState<Device>(getInitialDeviceState());
  const [editDevice, setEditDevice] = useState<Partial<Device>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    setLoading(true);
    setError(false);

    const timeout = setTimeout(() => {
      setLoading(false);
      setError(true);
      notification.error({
        message: "Error",
        description: "Failed to load devices. Please try again later.",
        placement: "top",
      });
    }, 5000);

    try {
      console.log("GET request to /devices");
      const response = await apiClient.get("/devices");
      clearTimeout(timeout);
      const devicesWithKey = response.data.map((device: any) => ({
        ...device,
        key: device.id,
      }));
      setDevices(devicesWithKey);
    } catch (error) {
      clearTimeout(timeout);
      setError(true);
      console.error("Error fetching devices:", error);
      notification.error({
        message: "Error",
        description: "Failed to load devices. Please try again later.",
        placement: "top",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeviceAction = async (
    method: string,
    url: string,
    data: Device | Partial<Device>,
    onSuccess: () => void
  ) => {
    try {
      let response;
      if (method === "post") {
        const modifiedData = { ...data };
        console.log("POST request to", url, "with data:", modifiedData);
        response = await apiClient.post(url, modifiedData);
      } else if (method === "put") {
        console.log("PUT request to", url, "with data:", data);
        response = await apiClient.put(url, data);
      } else {
        throw new Error(`Unsupported method: ${method}`);
      }
      setDevices((prevDevices) => {
        if (method === "post") {
          return [...prevDevices, { ...response.data, key: response.data.id }];
        }
        return prevDevices.map((device) =>
          device.key === data.key
            ? { ...response.data, key: response.data.id }
            : device
        );
      });
      onSuccess();
    } catch (error) {
      console.error(
        `Error ${method === "post" ? "adding" : "editing"} device:`,
        error
      );
      notification.error({
        message: `Error ${method === "post" ? "Adding" : "Editing"} Device`,
        description:
          "Something went wrong while changing the device data. Please try again.",
        placement: "top",
      });
    }
  };

  const handleAddDeviceOk = () => {
    const deviceData = {
      deviceName: newDevice.deviceName,
      status: newDevice.status,
      location: newDevice.location,
      relay1: newDevice.relay1,
      relay2: newDevice.relay2,
      relay3: newDevice.relay3,
      relay4: newDevice.relay4,
      lastSeen: newDevice.lastSeen,
    };

    handleDeviceAction("post", "/devices", deviceData, () => {
      setIsAddDeviceModalOpen(false);
      setNewDevice(getInitialDeviceState()); // Reset the new device state after adding
    });
  };

  const handleEditDeviceOk = () => {
    handleDeviceAction("put", `/devices/${editDevice?.key}`, editDevice, () => {
      setIsEditDeviceModalOpen(false);
    });
  };

  const handleDeleteDevice = async (key: string) => {
    try {
      console.log("DELETE request to /devices/" + key);
      await apiClient.delete(`/devices/${key}`);
      setDevices(devices.filter((device) => device.key !== key));
    } catch (error) {
      console.error("Error deleting device:", error);
      notification.error({
        message: "Error Deleting Device",
        description: "Failed to delete the device. Please try again later.",
        placement: "top",
      });
    }
  };

  const handleRelayChange = (value: string, relay: keyof Device) => {
    if (editDevice) {
      setEditDevice({
        ...editDevice,
        [relay]: value,
      });
    }
  };

  const handleStatusChange = (value: string) => {
    if (editDevice) {
      setEditDevice({
        ...editDevice,
        status: value,
      });
    }
  };

  const renderRelaySelect = (relay: keyof Device) => (
    <Select
      key={relay} // Add key prop here
      value={editDevice?.[relay]}
      onChange={(value) => handleRelayChange(value, relay)}
      style={{ width: "100%", marginBottom: 10 }}
    >
      <Option value="On">
        <CheckCircleOutlined style={{ color: "green", marginRight: 10 }} />
        On
      </Option>
      <Option value="Off">
        <CloseCircleOutlined style={{ color: "red", marginRight: 10 }} />
        Off
      </Option>
    </Select>
  );

  const renderDeviceModal = (isEdit: boolean) => (
    <Modal
      title={
        isEdit ? (
          <>
            <EditOutlined style={{ marginRight: 10 }} />
            Edit Device
          </>
        ) : (
          <>
            <PlusOutlined style={{ marginRight: 10 }} />
            Add New Device
          </>
        )
      }
      open={isEdit ? isEditDeviceModalOpen : isAddDeviceModalOpen}
      onOk={isEdit ? handleEditDeviceOk : handleAddDeviceOk}
      onCancel={
        isEdit
          ? () => setIsEditDeviceModalOpen(false)
          : () => setIsAddDeviceModalOpen(false)
      }
    >
      <Input
        placeholder="Device Name"
        value={isEdit ? editDevice?.deviceName : newDevice.deviceName}
        onChange={(e) => {
          if (isEdit) {
            setEditDevice({ ...editDevice, deviceName: e.target.value });
          } else {
            setNewDevice({ ...newDevice, deviceName: e.target.value });
          }
        }}
        style={{ marginBottom: 10 }}
      />
      <Input
        placeholder="Location"
        value={isEdit ? editDevice?.location : newDevice.location}
        onChange={(e) => {
          if (isEdit) {
            setEditDevice({ ...editDevice, location: e.target.value });
          } else {
            setNewDevice({ ...newDevice, location: e.target.value });
          }
        }}
        style={{ marginBottom: 10 }}
      />
      <Select
        value={isEdit ? editDevice?.status : newDevice.status}
        onChange={handleStatusChange}
        style={{ width: "100%", marginBottom: 10 }}
      >
        <Option value="Online">
          <WifiOutlined style={{ color: "green", marginRight: 10 }} />
          Online
        </Option>
        <Option value="Offline">
          <DisconnectOutlined style={{ color: "red", marginRight: 10 }} />
          Offline
        </Option>
      </Select>
      {["relay1", "relay2", "relay3", "relay4"].map((relay) =>
        renderRelaySelect(relay as keyof Device)
      )}
    </Modal>
  );

  return (
    <Layout style={{ padding: 20 }}>
      {/* Header with Title and Add Device Button */}
      <Row justify="space-between" style={{ marginBottom: 20 }}>
        <Col>
          <Title level={3}>Devices</Title>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setIsAddDeviceModalOpen(true)}
          >
            Add Device
          </Button>
        </Col>
      </Row>
      {/* Skeleton Loading */}
      {loading ? (
        <div style={styles.skeletonContainer}>
          <Skeleton active paragraph={{ rows: 4 }} />
        </div>
      ) : error ? (
        <div style={styles.skeletonContainer}>
          <Skeleton active paragraph={{ rows: 4 }} />
        </div>
      ) : (
        <Row gutter={[40, 25]}>
          {devices.map((device) => (
            <Col key={device.key} xs={24} sm={24} md={24} lg={8}>
              <Card
                title={device.deviceName}
                extra={
                  <div>
                    <Button
                      shape="circle"
                      icon={<EditOutlined />}
                      style={{ marginRight: "10px" }}
                      onClick={() => {
                        setEditDevice(device);
                        setIsEditDeviceModalOpen(true);
                      }}
                    />
                    <Button
                      shape="circle"
                      icon={<DeleteOutlined />}
                      onClick={() => handleDeleteDevice(device.key)}
                    />
                  </div>
                }
              >
                <Row>
                  <Col span={24}>
                    <Statistic
                      title="Status"
                      value={device.status}
                      valueStyle={{
                        color: device.status === "Online" ? "green" : "red",
                      }}
                      prefix={
                        device.status === "Online" ? (
                          <WifiOutlined style={{ color: "green" }} />
                        ) : (
                          <DisconnectOutlined style={{ color: "red" }} />
                        )
                      }
                    />
                  </Col>
                </Row>
                <Row>
                  <Col span={24}>
                    <Title level={5}>Location: {device.location}</Title>
                  </Col>
                </Row>
                <Row>
                  <Col span={24}>
                    <Title level={5}>Last Seen: {device.lastSeen}</Title>
                  </Col>
                </Row>
                <Row gutter={[8, 8]}>
                  {["relay1", "relay2", "relay3", "relay4"].map(
                    (relay, index) => (
                      <Col span={12} key={relay}>
                        <Title level={5}>{`Relay ${index + 1}`}</Title>
                        {device[relay as keyof Device] === "On" ? (
                          <CheckCircleOutlined
                            style={{ color: "blue", fontSize: "24px" }}
                          />
                        ) : (
                          <CloseCircleOutlined
                            style={{ color: "red", fontSize: "24px" }}
                          />
                        )}
                      </Col>
                    )
                  )}
                </Row>
              </Card>
            </Col>
          ))}
        </Row>
      )}
      {/* Modals */}
      {renderDeviceModal(false)} {/* Add Device Modal */}
      {renderDeviceModal(true)} {/* Edit Device Modal */}
    </Layout>
  );
};

const styles = {
  skeletonContainer: {
    padding: "20px",
    position: "fixed" as "fixed",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    zIndex: 1000,
    width: "50%",
    textAlign: "center" as "center",
  },
};

export default DevicePage;
